# sendmail using python smtplib
# https://github.com/sendgrid/sendgrid-python
import json,smtplib,socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

mail_config=json.load(open('config/sendmail.json'))
def send_message(message_to, mail_subject,mail_content):
    try:
        msg = MIMEMultipart()
        msg["Subject"] = mail_subject
        msg["From"] = mail_config["mail_from"]
        msg["To"] = message_to
        msg.attach(MIMEText(mail_content, "html"))
        server = smtplib.SMTP_SSL(mail_config["mail_smtp"], mail_config["mail_port"])
        server.ehlo()
        server.login(mail_config["mail_from"], mail_config["mail_pass"])
        server.sendmail(mail_config["mail_from"], message_to, msg.as_string())
        server.close()
        return True 
    except Exception as e:
        return e

def send_mail(mail_subject,mail_content):
    msg = MIMEMultipart()
    msg["Subject"] = mail_subject
    msg["From"] = mail_config["mail_from"]
    msg["To"] = mail_config["mail_to"]
    msg.attach(MIMEText(mail_content, "html"))
    server = smtplib.SMTP_SSL(mail_config["mail_smtp"], mail_config["mail_port"])
    server.ehlo()
    server.login(mail_config["mail_from"], mail_config["mail_pass"])
    server.sendmail(mail_config["mail_from"], mail_config["mail_to"], msg.as_string())
    server.close()
    return True