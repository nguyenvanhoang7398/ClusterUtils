import paramiko


class SshService(object):
    def ___init__(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def execute(self, host, command):
        self.client.connect(host)  # assume that ssh connection is password-less
        stdout = self.client.exec_command(command)[1]
        return stdout

    def close(self):
        self.client.close()
