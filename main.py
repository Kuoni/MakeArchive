import argparse
import os
import os.path

from MakeArchive import DirectoryNotFoundError
from MakeArchive import MakeArchive
from MakeArchive import ReadConfig

CONFIG_KEY = "config"
DISABLE_MAIL_KEY = "is_send_mail"
MAIL_CREDS_KEY = "send_mail"
PASSWORD_KEY = "pwd"


def send_mail(message, mail_creds_file_path):
    pass


def execute(exe_options):
    reader = ReadConfig(exe_options[CONFIG_KEY])
    dir_list = reader.read()

    is_use_password = os.path.exists(exe_options[PASSWORD_KEY])
    password = None
    if is_use_password:
        with open(exe_options[PASSWORD_KEY], "r") as fh:
            line = fh.readline()
            if line is not None:
                password = line

    make = MakeArchive(password)
    is_error = False
    msg = ""
    error_msg = "The process failed with message: {msg}"
    try:
        make.create_with_dirs(dir_list, os.getcwd(), r"F:\\test")
        msg = "Success {dirs_len} backup.".format(dirs_len=len(dir_list))
    except NotADirectoryError as ex:
        is_error = True
        msg = error_msg.format(msg=ex.filename)
    except DirectoryNotFoundError as ex:
        is_error = True
        msg = error_msg.format(msg=ex.message)
    except Exception:
        is_error = True
        msg = error_msg.format(msg="Generic Error, there may have been an error during copytree.")

    if not exe_options[DISABLE_MAIL_KEY]:
        send_mail(msg, exe_options[MAIL_CREDS_KEY])

if __name__ == "__main__":
    arg_parse = argparse.ArgumentParser(
        description="Copies folder given in a config list and zips them together finally" +
                    " it copies the zip to a final destination.")
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
    options = {CONFIG_KEY: the_args.config, DISABLE_MAIL_KEY: the_args.disable_mail,
               MAIL_CREDS_KEY: the_args.mail_creds, PASSWORD_KEY: the_args.password}

    execute(options)
