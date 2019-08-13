import constants
from prettytable import PrettyTable
import re


class Watcher(object):
    def __init__(self, ssh_service, email_service):
        self.ssh_service = ssh_service
        self.email_service = email_service

    def watch(self):
        gpu_stats = self.watch_gpu_stats()
        gpu_stats_table = self._tabular_gpu_stats(gpu_stats)
        self.email_service.send(constants.WATCHER_EMAIL_SUBJECT, content=gpu_stats_table)

    def watch_gpu_stats(self):
        host_gpu_stats = {}

        for host in constants.HOSTS:
            raw_tf_log_lines = self.ssh_service.execute(host,
                                                        "{} {}".format(constants.PYTHON_PATH,
                                                                       constants.CHECK_GPU_SCRIPT))

            # parse tf log
            start, end = 0, len(raw_tf_log_lines)
            for i, line in enumerate(raw_tf_log_lines):
                if constants.TF_LOG_START_MARKER in line:
                    start = i
                if constants.TF_LOG_END_MARKER in line:
                    end = i
            gpu_logs = raw_tf_log_lines[start: end + 1]
            host_gpu_stats[host] = self._parse_gpu_stats(gpu_logs)

        return host_gpu_stats

    @staticmethod
    def _tabular_gpu_stats(host_gpu_stats):
        header = ["Host name"]
        for gpu_num in range(constants.MAX_GPUS):
            header.append("GPU #{} - free".format(gpu_num))
            header.append("GPU #{} - total".format(gpu_num))

        table = PrettyTable(header)

        for host in constants.HOSTS:
            gpu_stats = host_gpu_stats[host]
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

    @staticmethod
    def _parse_gpu_stats(gpu_logs):
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
