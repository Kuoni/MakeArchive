# Import smtplib for the actual sending function
import smtplib

ADDR_FROM_MAIL_KEY = "addr_from"
ADDR_TO_MAIL_KEY = "addr_to"
MAIL_TITLE_KEY = "mail_title"
MAIL_MSG_KEY = "mail_msg"
LOGIN_USER_KEY = "username"
LOGIN_PASS_KEY = "pwd"


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
    print("Abort send mail, missing arguments.")