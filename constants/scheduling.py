WATCHER_PERIOD_MINUTE = 10
SCHEDULER_PERIOD_SECONDS = 30
MAX_GPUS = 2
GPU_THRESHOLD_GIB = 8.0
# HOSTS = ["xgpd0", "xgpd1", "xgpd2", "xgpd3", "xgpd4", "xgpd5", "xgpd6", "xgpd7", "xgpd8", "xgpd9"]
HOSTS = ["xgpe0", "xgpe1", "xgpe2", "xgpe3", "xgpe4", "xgpe5", "xgpe6", "xgpe7", "xgpe8", "xgpe9",
         "xgpf0", "xgpf1", "xgpf1", "xgpf2", "xgpf3", "xgpf4", "xgpf5", "xgpf6", "xgpf7", "xgpf8", "xgpf9", "xgpf10", "xgpf11"]
SCHEDULER_TMUX_NAME = "fyp"
# I tensorflow/core/common_runtime/gpu/gpu_device.cc:1411] Found device 1 with properties:
GPU_DEVICE_PATTERN = "\\| +(\\d+) + ([\\w ]+)\\|([\\w :.]+)\\|([\\w :/.]+)\\|"
# totalMemory: 11.75GiB freeMemory: 8.58GiB
GPU_MEMORY_PATTERN = "\\|([\\w %/:.]+)\\| +(\\w+) \\/ (\\w+) \\|([\\w %/:.]+)\\|"
SCHEDULING_EMAIL_SUBJECT = "Task successfully scheduled"
TF14_PYTHON_PATH = ""
