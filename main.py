import constants
from cores import EmailService, SshService, TaskManager, Watcher
import schedule
import time


if __name__ == "__main__":
    email_service = EmailService()
    ssh_service = SshService()
    watcher = Watcher(ssh_service, email_service)
    task_manager = TaskManager(constants.RESOURCE_ROOT, constants.HOSTS, ssh_service, email_service, watcher)
    schedule.every(constants.WATCHER_PERIOD_MINUTE).seconds.do(watcher.watch)
    # schedule.every(constants.SCHEDULER_PERIOD_MINUTE).seconds.do(task_manager.execute_pending_tasks)
    while True:
        schedule.run_pending()
        time.sleep(1)
