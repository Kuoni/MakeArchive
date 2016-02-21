# Import smtplib for the actual sending function
import os.path
import smtplib

import unittest

ADDR_FROM_MAIL_KEY = "addr_from"
ADDR_TO_MAIL_KEY = "addr_to"
MAIL_TITLE_KEY = "mail_title"
MAIL_MSG_KEY = "mail_msg"
LOGIN_USER_KEY = "username"
LOGIN_PASS_KEY = "pwd"

TIMESTAMP_START_KEY = "ts_start"
TIMESTAMP_END_KEY = "ts_end"

msg_success_template = "Success {dir_count} archived.\nFolders are:\n{dir_list}\n" + \
                    "Process Started at: {time_start}\nProcess Ended at: {time_end}\n" + \
                    "File Count: {files} - Folder Count: {folders}"


class TestMsgReport(unittest.TestCase):
    def testTemplate(self):
        folders = [r"C:\folders\folderA", r"C:\folders\folderB", r"C:\folders\folderC"]
        msg_check = "Hey, 3, folders are:\nfolderA\nfolderB\nfolderC\n " +\
                    "proc start: 11/01/2016 proc end: 12/01/2016 files: 3 - folders: 4."
        msg_temp = "Hey, {dir_count}, folders are:\n{dir_list}\n proc start: {time_start} " + \
                   "proc end: {time_end} files: {files} - folders: {folders}."

        time_dict = {TIMESTAMP_START_KEY: "11/01/2016", TIMESTAMP_END_KEY: "12/01/2016"}
        self.assertEquals(msg_check, make_report(msg_temp, folders, time_dict, 3, 4))


def make_report(msg_template, dir_list, time_dict, file_count, folder_count):
    dir_names_list = list()
    for a_dir in dir_list:
        dir_name = os.path.split(a_dir)[1]
        dir_names_list.append(dir_name)

    dir_str = "\n".join(dir_names_list)

    msg = msg_template.format(dir_count=len(dir_list), dir_list=dir_str, time_start=time_dict[TIMESTAMP_START_KEY],
                              time_end=time_dict[TIMESTAMP_END_KEY], files=file_count, folders=folder_count)
    return msg


def send_mail(addr_dict, msg_dict, login_dict):
    me = addr_dict[ADDR_FROM_MAIL_KEY]
    you = addr_dict[ADDR_TO_MAIL_KEY]

    msg = "\r\n".join([
        "From: {me}".format(me=me),
        "To: {you}".format(you=you),
        "Subject: {title}".format(title=msg_dict[MAIL_TITLE_KEY]),
        "",
        "{msg}".format(msg=msg_dict[MAIL_MSG_KEY])
    ])

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP('smtp.gmail.com:587')
    s.ehlo()
    s.starttls()
    s.login(login_dict[LOGIN_USER_KEY], login_dict[LOGIN_PASS_KEY])
    s.sendmail(me, [you], msg)
    s.quit()


if __name__ == "__main__":
    unittest.main()
