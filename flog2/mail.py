# sendmail using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import json
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from skipconfig import sg_config
def send_mail(mail_subject,mail_content):
    try:
        message = Mail(
            from_email=sg_config["sg_from"],
            to_emails=sg_config["sg_to"],
            subject=mail_subject,html_content=mail_content)
        grid = SendGridAPIClient(sg_config["sg_key"])
        response = grid.send(message)
        return response
    except Exception as e:
        return False

def send_message(message_to,mail_subject,message_content):
    try:
        message = Mail(
            from_email=sg_config["sg_from"],
            to_emails=message_to,
            subject=mail_subject,html_content=message_content)
        grid = SendGridAPIClient(sg_config["sg_key"])
        response = grid.send(message)
        return response
    except Exception as e:
        return False