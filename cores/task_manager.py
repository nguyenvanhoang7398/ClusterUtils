import constants
import logging
import os
import utils as utils


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
        logging.debug("Pending tasks " + str(pending_tasks))
        pending_gpu_tasks = []

        for task_id, task in pending_tasks.items():
            task_resource = task["resource"]
            if task_resource == "gpu":
                pending_gpu_tasks.append(task_id)
            else:
                logging.warning("Unrecognized resource '{}'".format(task_resource))

        logging.debug("Pending gpu tasks " + str(pending_gpu_tasks))
        next_pending_tasks = dict(pending_tasks)
        host_gpu_task_map = self._map_host_with_gpu_tasks(pending_gpu_tasks)
        logging.debug("Host gpu task map " + str(host_gpu_task_map))
        for host, (gpu_num, task_id) in host_gpu_task_map.items():
            task = pending_tasks[task_id]
            self.ssh_service.execute(host, task["command"])
            logging.debug("Executed task with id {}".format(task_id))
            del next_pending_tasks[task_id]

        next_pending_task_dict = {
            "tasks": next_pending_tasks
        }

        utils.write_json(next_pending_task_dict, pending_task_path)

    def _map_host_with_gpu_tasks(self, pending_tasks):
        host_gpu_task_map = {}
        host_gpu_stats = self.watcher.watch_gpu_stats()
        logging.debug("Host gpu stats " + str(host_gpu_stats))
        num_allocated_tasks = 0
        for host, gpu_stats in host_gpu_stats.items():
            if host not in host_gpu_task_map:
                available_gpu_num = self.check_free_gpu(gpu_stats, constants.GPU_THRESHOLD_GIB)
                logging.debug("Device {} is available in {}".format(available_gpu_num, host))
                if available_gpu_num >= 0:
                    host_gpu_task_map[host] = (available_gpu_num, pending_tasks[num_allocated_tasks])
                    num_allocated_tasks += 1
        return host_gpu_task_map

    @staticmethod
    def check_free_gpu(gpu_stats, gpu_threshold_gib):
        for gpu_num, stats in gpu_stats.items():
            free_mem = stats["free_memory"]
            logging.debug("Raw free memory is " + str(free_mem))
            if "MiB" in free_mem:
                free_mem = float(free_mem[:-3]) / 1024
            elif "GiB" in free_mem:
                free_mem = float(free_mem[:-3])
            else:
                logging.warning("Unrecognized memory unit '{}'".format(free_mem))
                free_mem = 0
            logging.debug("Parsed free memory is {}, threshold {}".format(str(free_mem), str(gpu_threshold_gib)))
            if free_mem > gpu_threshold_gib:
                return gpu_num
        return -1
