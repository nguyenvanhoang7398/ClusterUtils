import constants
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import schedule
import smtplib
import socket
from string import Template
from subprocess import Popen, PIPE
import time


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


def watch_tf_gpu():
    check_gpu_result = Popen(["python", constants.CHECK_GPU_SCRIPT], shell=False, stderr=PIPE, bufsize=1)
    raw_tf_log_lines = []
    for line in iter(check_gpu_result.stderr.readline, b''):
        raw_tf_log_lines.append(line.decode("utf-8"))

    # parse tf log
    start, end = 0, len(raw_tf_log_lines)
    for i, line in enumerate(raw_tf_log_lines):
        if constants.TF_LOG_START_MARKER in line:
            start = i
        if constants.TF_LOG_END_MARKER in line:
            end = i
    return "".join(raw_tf_log_lines[start: end+1])


def watch(email_service):
    tf_gpu_content = watch_tf_gpu()
    email_service.send(constants.WATCHER_EMAIL_SUBJECT, tf_gpu_content=tf_gpu_content)


if __name__ == "__main__":
    watcher_email_service = EmailService()
    schedule.every(constants.WATCHER_PERIOD_MINUTE).minutes.do(watch, watcher_email_service)

    while True:
        schedule.run_pending()
        time.sleep(1)
