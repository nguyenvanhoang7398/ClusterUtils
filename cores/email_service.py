import constants
import smtplib
import socket
from string import Template
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmailService(object):
    def __init__(self):
        self.email_service = smtplib.SMTP(host=constants.SMTP_HOST, port=constants.SMTP_PORT)
        self.email_service.starttls()
        self.email_service.login(constants.NOTIFICATION_EMAIL, constants.NOTIFICATION_PASSWORD)
        self.email_template = self.read_template(constants.EMAIL_TEMPLATE)

    @staticmethod
    def read_template(filename):
        with open(filename, 'r', encoding='utf-8') as template_file:
            template_file_content = template_file.read()
        return Template(template_file_content)

    def send(self, subject, tf_gpu_content):
        message = MIMEMultipart()

        current_time = datetime.datetime.now()

        email_content = self.email_template.substitute(TIMESTAMP=str(current_time), HOST=str(socket.gethostname()),
                                                       TENSORFLOW_GPU=str(tf_gpu_content))
        print(email_content)

        message['From'] = constants.NOTIFICATION_EMAIL
        message['To'] = constants.RECEIVING_EMAIL
        message['Subject'] = subject
        message.attach(MIMEText(email_content, 'plain'))
        self.email_service.send_message(message)
        del message

    def close(self):
        self.email_service.close()
