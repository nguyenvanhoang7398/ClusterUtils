import paramiko


class SshService(object):
    def __init__(self):
        pass

    def execute(self, host, command):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(host)  # assume that ssh connection is password-less
        stdout = client.exec_command(command, get_pty=True)[1]
        client.close()
        return [str(m) for m in stdout]
