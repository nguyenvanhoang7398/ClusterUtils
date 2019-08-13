import constants
from cores import EmailService, SshService
from prettytable import PrettyTable
import re
import schedule
from subprocess import Popen, PIPE
import time


def watch_gpu_stats():
    ssh_service = SshService()

    header = ["Host name"]
    for gpu_num in range(constants.MAX_GPUS):
        header.append("GPU #{} - free".format(gpu_num))
        header.append("GPU #{} - total".format(gpu_num))

    table = PrettyTable(header)

    for host in constants.HOSTS:
        raw_tf_log_lines = ssh_service.execute(host, "{} {}".format(constants.PYTHON_PATH, constants.CHECK_GPU_SCRIPT))

        # parse tf log
        start, end = 0, len(raw_tf_log_lines)
        for i, line in enumerate(raw_tf_log_lines):
            if constants.TF_LOG_START_MARKER in line:
                start = i
            if constants.TF_LOG_END_MARKER in line:
                end = i
        gpu_logs = raw_tf_log_lines[start: end+1]
        gpu_stats = parse_gpu_stats(gpu_logs)
        table_row = [host]
        for gpu_num in range(constants.MAX_GPUS):
            if gpu_num < len(gpu_stats):
                table_row.append(gpu_stats[gpu_num]["free_memory"])
                table_row.append(gpu_stats[gpu_num]["total_memory"])
            else:
                table_row.append("")
                table_row.append("")
        table.add_row(table_row)

    return str(table)


def parse_gpu_stats(gpu_logs):
    gpu_stats = []
    parsed_gpu_device = None
    for line in gpu_logs:
        captured_device_group = re.search(constants.GPU_DEVICE_PATTERN, line)
        if captured_device_group is not None:
            parsed_gpu_device = captured_device_group.group(2)

        captured_memory_group = re.search(constants.GPU_MEMORY_PATTERN, line)
        if captured_memory_group is not None:
            assert parsed_gpu_device is not None, "No device is being parsed"
            free_memory, total_memory = captured_memory_group.group(2), captured_memory_group.group(1)
            gpu_stats.append({
                "device_number": parsed_gpu_device,
                "free_memory": free_memory,
                "total_memory": total_memory
            })
    return gpu_stats


def watch():
    tf_gpu_content = watch_gpu_stats()
    watcher_email_service = EmailService()
    watcher_email_service.send(constants.WATCHER_EMAIL_SUBJECT, tf_gpu_content=tf_gpu_content)


if __name__ == "__main__":
    schedule.every(constants.WATCHER_PERIOD_MINUTE).minutes.do(watch)
    while True:
        schedule.run_pending()
        time.sleep(1)
