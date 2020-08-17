# sendmail using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import json,os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
sg_config=json.load(open('config/sendgrid.json'))
def send_mail(mail_subject,mail_content):
    try:
        message = Mail(
            from_email='admin@skipflog.appspotmail.com',
            to_emails='skipflog@googlegroups.com',
            subject=mail_subject,html_content=mail_content)
        grid = SendGridAPIClient(sg_config["sg_key"])
        response = grid.send(message)
        return True
    except Exception as e:
        return False

def send_message(message_to,message_content):
    try:
        message = Mail(
            from_email='admin@skipflog.appspotmail.com',
            to_emails=message_to,
            subject=mail_subject,html_content=mail_content)
        grid = SendGridAPIClient(sg_config["sg_key"])
        response = grid.send(message)
        return True
    except Exception as e:
        return False