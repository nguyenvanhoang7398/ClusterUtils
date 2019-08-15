WATCHER_PERIOD_MINUTE = 10
SCHEDULER_PERIOD_MINUTE = 10
MAX_GPUS = 5
GPU_THRESHOLD_GIB = 2.0
# HOSTS = ["xgpd0", "xgpd1", "xgpd2", "xgpd3", "xgpd4", "xgpd5", "xgpd6", "xgpd7", "xgpd8", "xgpd9"]
HOSTS = ["xgpd0", "xgpe0", "xgpf0"]
SCHEDULER_TMUX_NAME = "fyp"
# I tensorflow/core/common_runtime/gpu/gpu_device.cc:1411] Found device 1 with properties:
GPU_DEVICE_PATTERN = "\\| +(\\d+) + ([\\w ]+)\\|([\\w :.]+)\\|([\\w :.]+)\\|"
# totalMemory: 11.75GiB freeMemory: 8.58GiB
GPU_MEMORY_PATTERN = "\\|([\\w %/:.]+)\\| +(\\w+) / (\\w+) \\|([\\w %/:.]+)\\|"
SCHEDULING_EMAIL_SUBJECT = "Task successfully scheduled"
