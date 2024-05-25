# sendmail using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import json,smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_message(message_to,mail_subject,message_content):
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail, Content
        sg_config=json.load(open('config/sendgrid.json'))
        message = Mail(
            from_email=sg_config["sg_from"],
            to_emails=message_to,
            subject=mail_subject,html_content=message_content)
        grid = SendGridAPIClient(sg_config["sg_key"])
        response = grid.send(message)
        return response
    except Exception as e:
        return False

# send mail using smtp library 
def smtp_email(message_to,mail_subject,message_content):
    try:
        sm_config=json.load(open('config/sendmail.json'))
    except:
        from models import get_document
        sm_config=get_document('messages','config')
    msg = MIMEMultipart('alternative')
    html = MIMEText(message_content,"html")
    msg['Subject'] = mail_subject
    msg['From'] = sm_config["sm_from"]
    msg['To'] = message_to
    msg.attach(html)
    with smtplib.SMTP_SSL(sm_config["sm_server"], sm_config["sm_port"]) as smtp_server:
       smtp_server.login(msg["From"], sm_config["sm_pass"])
       smtp_server.sendmail(msg["From"], msg["To"], msg.as_string())
    return True

# send mail to multiple recipients		
def send_mail(mail_subject,mail_content):
    for sm_to_email in sm_config["sm_to"]:
        smtp_email(sm_to_email,mail_subject,mail_content)
    return True

