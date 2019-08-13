WATCHER_PERIOD_MINUTE = 1
SCHEDULER_PERIOD_MINUTE = 1
MAX_GPUS = 5
GPU_THRESHOLD_GIB = 2.0
HOSTS = ["xgpd0", "xgpd1", "xgpd2", "xgpd3", "xgpd4", "xgpd5", "xgpd6", "xgpd7", "xgpd8", "xgpd9"]
SCHEDULER_TMUX_NAME = "fyp"
# I tensorflow/core/common_runtime/gpu/gpu_device.cc:1411] Found device 1 with properties:
GPU_DEVICE_PATTERN = "^(.+) Found device (\\d) with properties"
# totalMemory: 11.75GiB freeMemory: 8.58GiB
GPU_MEMORY_PATTERN = "^totalMemory: (\\w.+) freeMemory: (\\w.+)\\r\\n"
