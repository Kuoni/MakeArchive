# Import smtplib for the actual sending function
import smtplib

# Import the email modules we'll need
from email.mime.text import MIMEText


def send_mail():
    me = "" #ibabinruel
    you = '' #perso
    msg_d = dict()
    msg_d['Subject'] = 'Simple GMail Python Test with Archive job result'
    msg_d['From'] = me
    msg_d['To'] = you

    msg = "\r\n".join([
        "From: {me}".format(me=me),
        "To: {you}".format(you=you),
        "Subject: {title}".format(title=msg_d['Subject']),
        "",
        "This is a test that will show the result of my new Archive to Google Docs."
    ])

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP('smtp.gmail.com:587')
    s.ehlo()
    s.starttls()
    s.login("", "")
    s.sendmail(me, [you], msg)
    s.quit()


if __name__ == "__main__":
    send_mail()