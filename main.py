import argparse
import datetime
import logging
import os
import os.path
import re

import mailReport

from MakeArchive import CleanUpError
from MakeArchive import DirectoryNotFoundError
from MakeArchive import MakeArchive
from MakeArchive import ReadConfig

CONFIG_KEY = "config"
DISABLE_MAIL_KEY = "is_send_mail"
MAIL_CREDS_KEY = "send_mail"
PASSWORD_KEY = "pwd"
DEST_PATH_KEY = "dest"
WORK_PATH_KEY = "work"


def parse_mail_creds(creds_path):
    res_dict = None
    if os.path.exists(creds_path):
        res_dict = dict()
        with open(creds_path, 'r') as fh:
            lines = fh.readlines()
            patt_from = re.compile(r"^From: (.+)$")
            patt_to = re.compile(r"^To: (.+)$")
            patt_user = re.compile(r"UN: (.+)$")
            patt_pwd = re.compile(r"PWD: (.+)$")

            for line in lines:
                res_from = patt_from.match(line)
                res_to = patt_to.match(line)
                res_user = patt_user.match(line)
                res_pwd = patt_pwd.match(line)

                if res_from and len(res_from.groups()) > 0:
                    res_dict[mailReport.ADDR_FROM_MAIL_KEY] = res_from.groups()[0]

                if res_to and len(res_to.groups()) > 0:
                    res_dict[mailReport.ADDR_TO_MAIL_KEY] = res_to.groups()[0]

                if res_user and len(res_user.groups()) > 0:
                    res_dict[mailReport.LOGIN_USER_KEY] = res_user.groups()[0]

                if res_pwd and len(res_pwd.groups()) > 0:
                    res_dict[mailReport.LOGIN_PASS_KEY] = res_pwd.groups()[0]

    return res_dict


def send_mail(title, message, mail_creds_file_path):
    """
    Send email to inform the user that the task has completedw
    :param title: string: title of email.
    :param message: string: message body of email.
    :param mail_creds_file_path: 4 keys inside mail file, in order, one per line:
     from email, to email, username to send, password to send.
    :return: False if failed to send, True otherwise.
    """
    addr_dict = dict()
    login_dict = dict()
    temp_dict = parse_mail_creds(mail_creds_file_path)
    if temp_dict is not None:
        addr_dict[mailReport.ADDR_FROM_MAIL_KEY] = temp_dict[mailReport.ADDR_FROM_MAIL_KEY]
        addr_dict[mailReport.ADDR_TO_MAIL_KEY] = temp_dict[mailReport.ADDR_TO_MAIL_KEY]

        login_dict[mailReport.LOGIN_USER_KEY] = temp_dict[mailReport.LOGIN_USER_KEY]
        login_dict[mailReport.LOGIN_PASS_KEY] = temp_dict[mailReport.LOGIN_PASS_KEY]
    else:
        return False

    msg_dict = dict()
    msg_dict[mailReport.MAIL_TITLE_KEY] = title
    msg_dict[mailReport.MAIL_MSG_KEY] = message
    mailReport.send_mail(addr_dict, msg_dict, login_dict)

    return True


def parse_zip_pwd(pwd_file_path):
    is_use_password = os.path.exists(pwd_file_path)
    password = None
    if is_use_password:
        with open(pwd_file_path, "r") as fh:
            line = fh.readline()
            if line is not None:
                password = line

    return password


def get_timestamp_logfile_str():
    return get_now_timestamp().strftime("%Y_%m_%d")


def get_now_timestamp():
    return datetime.datetime.now()


def execute(exe_options):
    reader = ReadConfig(exe_options[CONFIG_KEY])
    dir_list = reader.read()

    logging.info("Parsing Password")
    password = parse_zip_pwd(exe_options[PASSWORD_KEY])
    make = MakeArchive(password)
    is_error = False
    msg = ""
    error_msg = "The process failed with message: {msg}"
    try:
        logging.info("Calling Make Archive archiving function")
        files, folders = make.create_with_dirs(dir_list,
                                               exe_options[WORK_PATH_KEY], exe_options[DEST_PATH_KEY])
        msg = "Success {dirs_len} backup. \n Files: {files}; Folders {folders}".format(
            dirs_len=len(dir_list), files=files, folders=folders)
        logging.debug("Archive Success")
    except NotADirectoryError as ex:
        is_error = True
        msg = error_msg.format(msg=ex.filename)
        logging.info("Error path is not a directory. {msg}".format(msg=ex.filename))
    except DirectoryNotFoundError as ex:
        is_error = True
        msg = error_msg.format(msg=ex.message)
        logging.info("Error directory not found. {msg}".format(msg=ex.message))
    except CleanUpError as ex:
        logging.info("Problem cleaning work folder.")
    except Exception:
        is_error = True
        msg = error_msg.format(msg="Generic Error, there may have been an error during copytree.")
        logging.info("Error: Generic Error, could happen during shutil copytree.")

    if not exe_options[DISABLE_MAIL_KEY]:
        logging.info("Sending mail...")

        title = "Backup Butler: A new backup has been delivered"
        if is_error:
            title = "Backup Butler: Backup task failed"
        mail_ret = send_mail(title, msg, exe_options[MAIL_CREDS_KEY])
        if mail_ret:
            logging.info("... mail sent.")
        else:
            logging.info("... error while trying to send mail!")

    logging.info("Task completed.")

if __name__ == "__main__":
    logging.basicConfig(filename="{stamp}_run.log".format(stamp=get_timestamp_logfile_str()),
                        level=logging.DEBUG, format='%(asctime)s %(message)s')
    logging.info("Task started.")
    arg_parse = argparse.ArgumentParser(
        description="Copies folder given in a config list and zips them together finally" +
                    " it copies the zip to a final destination.")
    arg_parse.add_argument("dest_path", help="Where the archive should be copied to. Another drive or a remote drive.")
    arg_parse.add_argument("-c", "--config", dest="config", default="config.txt",
                           help="specify this flag if you want to have the config read from somewhere else.")
    arg_parse.add_argument("-e", "--email_disable", dest="disable_mail", default=False,
                           action="store_true",
                           help="Toggle this if you don't want an email to be sent once the back is created.")
    arg_parse.add_argument("-m", "--mail_creds", dest="mail_creds", default="mail.txt",
                           help="SMTP info: first line: username, second line: password")
    arg_parse.add_argument("-p", "--password", dest="password", default="password.txt",
                           help="file with one line: a password. No file means no password.")
    arg_parse.add_argument("-w", "--work_folder", dest="work_path", default=os.getcwd(),
                           help="Changes where the script works. Default is current directory.")

    the_args = arg_parse.parse_args()
    options = {DEST_PATH_KEY: the_args.dest_path, CONFIG_KEY: the_args.config,
               DISABLE_MAIL_KEY: the_args.disable_mail,
               MAIL_CREDS_KEY: the_args.mail_creds, PASSWORD_KEY: the_args.password,
               WORK_PATH_KEY: the_args.work_path}

    execute(options)
