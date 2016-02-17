import argparse
import datetime
import logging
import os
import os.path

from MakeArchive import CleanUpError
from MakeArchive import DirectoryNotFoundError
from MakeArchive import MakeArchive
from MakeArchive import ReadConfig

CONFIG_KEY = "config"
DISABLE_MAIL_KEY = "is_send_mail"
MAIL_CREDS_KEY = "send_mail"
PASSWORD_KEY = "pwd"
DEST_PATH_KEY = "dest"


def send_mail(message, mail_creds_file_path):
    logging.info("... Mail system not implemented.")


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
        make.create_with_dirs(dir_list, os.getcwd(), exe_options[DEST_PATH_KEY])
        msg = "Success {dirs_len} backup.".format(dirs_len=len(dir_list))
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
        send_mail(msg, exe_options[MAIL_CREDS_KEY])

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

    the_args = arg_parse.parse_args()
    options = {DEST_PATH_KEY: the_args.dest_path, CONFIG_KEY: the_args.config,
               DISABLE_MAIL_KEY: the_args.disable_mail,
               MAIL_CREDS_KEY: the_args.mail_creds, PASSWORD_KEY: the_args.password}

    execute(options)
