import paramiko
import uuid


class SshService(object):
    def __init__(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def execute(self, host, command):
        try:
            self.client.connect(host)  # assume that ssh connection is password-less
            stdout = self.client.exec_command(command, get_pty=True)[1]
            return [str(m) for m in stdout]
        except paramiko.SSHException as e:
            print(e)
        return []

    def async_execute(self, host, command, log_path=None, working_dir="/home/v/vanhoang"):
        cmd_template = "cd {}; " \
                       "nohup {} >> {} 2>&1 &"
        if log_path is None:
            log_path = "/tmp/scheduler_task_{}".format(str(uuid.uuid1()))
        try:
            self.client.connect(host)
            transport = self.client.get_transport()
            channel = transport.open_session()
            command_full = cmd_template.format(working_dir, command, log_path)
            channel.exec_command(command_full)
            return log_path
        except paramiko.SSHException as e:
            print(e)
        return ""

    def close(self):
        self.client.close()
