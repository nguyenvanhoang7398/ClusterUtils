import constants
import logging
import os
from prettytable import PrettyTable
import utils as utils
logging.basicConfig(level=logging.INFO)


class TaskManager(object):
    def __init__(self, resource_root, hosts, ssh_service, email_service, watcher):
        self.resource_root = resource_root
        self.hosts = hosts
        self.ssh_service = ssh_service
        self.email_service = email_service
        self.watcher = watcher

    def execute_pending_tasks(self):
        pending_task_path = os.path.join(self.resource_root, "pending_tasks.json")
        pending_tasks = utils.read_json(pending_task_path)["tasks"]
        logging.info("Pending tasks " + str(pending_tasks))
        pending_gpu_tasks = []

        for task_id, task in pending_tasks.items():
            task_resource = task["resource"]
            if task_resource == "gpu":
                pending_gpu_tasks.append(task_id)
            else:
                logging.warning("Unrecognized resource '{}'".format(task_resource))

        logging.info("Pending gpu tasks " + str(pending_gpu_tasks))

        if len(pending_gpu_tasks) > 0:
            next_pending_tasks = dict(pending_tasks)
            host_gpu_task_map = self._map_host_with_gpu_tasks(pending_gpu_tasks)
            logging.info("Host gpu task map " + str(host_gpu_task_map))
            for host, (gpu_num, task_id) in host_gpu_task_map.items():
                task = pending_tasks[task_id]
                command, log_path = task["command"], task["log_path"] \
                    if "log_path" in task and len(task["log_path"]) > 0 else None
                log_path = self.ssh_service.async_execute(host, command, log_path)
                if log_path is not None:
                    logging.info("Executed task with id {}, writing to log at path {}".format(task_id, log_path))
                    scheduled_task_table = self._tabular_scheduled_task(command, "gpu", log_path, host)
                    self.email_service.send(constants.SCHEDULING_EMAIL_SUBJECT, content=scheduled_task_table)
                    del next_pending_tasks[task_id]

            next_pending_task_dict = {
                "tasks": next_pending_tasks
            }

            utils.write_json(next_pending_task_dict, pending_task_path)

    @staticmethod
    def _tabular_scheduled_task(command, resource, log_path, host):
        table = PrettyTable(["Command", "Resource", "Log", "Host"])
        table.add_row([command, resource, log_path, host])
        print(table)
        return str(table)

    def _map_host_with_gpu_tasks(self, pending_tasks):
        host_gpu_task_map = {}
        host_gpu_stats = self.watcher.watch_gpu_stats()
        logging.info("Host gpu stats " + str(host_gpu_stats))
        num_allocated_tasks = 0
        for host, gpu_stats in host_gpu_stats.items():
            if num_allocated_tasks >= len(pending_tasks):
                break
            if host not in host_gpu_task_map:
                available_gpu_num = self.check_free_gpu(gpu_stats, constants.GPU_THRESHOLD_GIB)
                logging.info("Device {} is available in {}".format(available_gpu_num, host))
                if int(available_gpu_num) >= 0:
                    host_gpu_task_map[host] = (available_gpu_num, pending_tasks[num_allocated_tasks])
                    num_allocated_tasks += 1
        return host_gpu_task_map

    @staticmethod
    def check_free_gpu(gpu_stats, gpu_threshold_gib):
        logging.info("gpu stats " + str(gpu_stats))
        for stats in gpu_stats:
            gpu_num = stats["device_number"]
            free_mem = stats["free_memory"]
            logging.info("Raw free memory is " + str(free_mem))
            if "MiB" in free_mem:
                free_mem = float(free_mem[:-3]) / 1024
            elif "GiB" in free_mem:
                free_mem = float(free_mem[:-3])
            else:
                logging.warning("Unrecognized memory unit '{}'".format(free_mem))
                free_mem = 0
            logging.info("Parsed free memory is {}, threshold {}".format(str(free_mem), str(gpu_threshold_gib)))
            if free_mem > gpu_threshold_gib:
                return gpu_num
        return -1
