import paramiko


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

    def close(self):
        self.client.close()
