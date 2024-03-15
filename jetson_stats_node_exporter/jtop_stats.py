import psutil
from jtop import jtop


class JtopObservable(object):

    def __init__(self, update_period=0.5):
        self.data = {}

        with jtop(interval=update_period) as jetson:
            self.jetson = jetson

    def read_stats(self):
        self.data = {
            "stats": self.jetson.stats,
            "board": self.jetson.board,
            "cpu": self.jetson.cpu,
            "mem": self.jetson.memory,
            "gpu": self.jetson.gpu,
            # "iram": self.jetson.iram,
            "pwr": self.jetson.power,
            # "swp": self.jetson.swap,
            "tmp": self.jetson.temperature,
            "upt": self.jetson.uptime
        }

        return self.data

    def get_storage_info(self):
        partitions = psutil.disk_partitions()
        unit = "GB"
        unit_factor = 1_000_000_000

        self.storage_data = {}
        for partition in partitions:
            disk_use = psutil.disk_usage(partition.mountpoint)._asdict()
            if partition.mountpoint not in self.storage_data.keys():
                self.storage_data[partition.mountpoint] = {}

            for metric, value in disk_use.items():
                self.storage_data[partition.mountpoint][metric] = value / unit_factor  # Conversion from B to GB

        return self.storage_data, unit
