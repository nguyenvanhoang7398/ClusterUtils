import constants
import logging
from prettytable import PrettyTable
import re


logging.basicConfig(level=logging.INFO)


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
        start_pattern = re.compile(constants.TF_LOG_START_MARKER)
        end_pattern = re.compile(constants.TF_LOG_END_MARKER)

        for host in constants.HOSTS:
            logging.info("Gpu stats command {}, host {}".format(constants.GPU_STATS_COMMAND, host))
            raw_tf_log_lines = self.ssh_service.execute(host, constants.GPU_STATS_COMMAND)
            logging.info("Raw tf log " + str(raw_tf_log_lines))
            # parse tf log
            start, end = 0, len(raw_tf_log_lines)
            for i, line in enumerate(raw_tf_log_lines):
                if start_pattern.match(line):
                    start = i
                if end_pattern.match(line):
                    end = i
            gpu_logs = raw_tf_log_lines[start: end]
            host_gpu_stats[host] = self.parse_gpu_stats(gpu_logs)

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
    def parse_gpu_stats(gpu_logs):
        gpu_stats = []
        parsed_gpu_device = None
        for line in gpu_logs:
            captured_device_group = re.search(constants.GPU_DEVICE_PATTERN, line)
            if captured_device_group is not None:
                parsed_gpu_device = captured_device_group.group(1)

            captured_memory_group = re.search(constants.GPU_MEMORY_PATTERN, line)
            if captured_memory_group is not None:
                assert parsed_gpu_device is not None, "No device is being parsed"
                used_memory, total_memory = captured_memory_group.group(2), captured_memory_group.group(3)
                free_memory = str(int(total_memory[:-3]) - int(used_memory[:-3])) + "MiB"
                gpu_stats.append({
                    "device_number": parsed_gpu_device,
                    "free_memory": free_memory,
                    "total_memory": total_memory
                })

        return gpu_stats
