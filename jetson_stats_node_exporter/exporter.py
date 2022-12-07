from prometheus_client.core import GaugeMetricFamily
from .logger import factory
from .jtop_stats import JtopObservable


class Jetson(object):
    def __init__(self, interval=10):

        if float(interval) < 0.5:
            raise BlockingIOError("Jetson Stats only works with 0.5s monitoring intervals and slower.")

        self.jtop_observer = JtopObservable(interval=0.5)  # seconds. 0.5 sec Standard for jtop.
        self.jtop_stats = {}
        self.disk = {}
        self.disk_units = "GB"
        self.interval = interval

    def update(self):
        self.jtop_stats = self.jtop_observer.read_stats()
        self.disk, self.disk_units = self.jtop_observer.get_storage_info()


class JetsonExporter(object):
    def __init__(self, interval):
        self.jetson = Jetson(interval)
        self.logger = factory(__name__)

    def __cpu(self):
        cpu_gauge = GaugeMetricFamily(
            name="cpu",
            documentation="CPU Statistics from Jetson Stats (ARMv8 Processor rev 1 (v8l))",
            labels=["core", "statistic"],
            unit="Hz"
        )
        for cpu_name, core_data in self.jetson.jtop_stats["cpu"].items():
            core_number = cpu_name.replace("CPU", "")
            # cpu_gauge.add_metric([core_number, "status"], value=core_data["val"])
            cpu_gauge.add_metric([core_number, "freq"], value=core_data["frq"])
            cpu_gauge.add_metric([core_number, "min_freq"], value=core_data["min_freq"])
            cpu_gauge.add_metric([core_number, "max_freq"], value=core_data["max_freq"])
            cpu_gauge.add_metric([core_number, "val"], value=core_data["val"])
        return cpu_gauge

    def __gpu(self):
        gpu_gauge = GaugeMetricFamily(
            name="gpu_utilization_percentage",
            documentation="GPU Statistics from Jetson Stats",
            labels=["statistic", "nvidia_gpu"],
            unit="Hz"
        )
        gpu_gauge.add_metric(["Nvidia Maxwell", "freq"], value=self.jetson.jtop_stats["gpu"]["frq"])
        gpu_gauge.add_metric(["Nvidia Maxwell", "min_freq"], value=self.jetson.jtop_stats["gpu"]["min_freq"])
        gpu_gauge.add_metric(["Nvidia Maxwell", "max_freq"], value=self.jetson.jtop_stats["gpu"]["max_freq"])
        return gpu_gauge

    def __iram(self):
        iram_gauge = GaugeMetricFamily(
            name="iram",
            documentation=f"Video Memory Statistics from Jetson Stats (unit: {self.jetson.jtop_stats['iram']['unit']}B)",
            labels=["statistic", "nvidia_gpu"],
            unit="kB"
        )
        iram_gauge.add_metric(["Nvidia Maxwell", "used"], value=self.jetson.jtop_stats["iram"]["use"])
        iram_gauge.add_metric(["Nvidia Maxwell", "total"], value=self.jetson.jtop_stats["iram"]["tot"])
        return iram_gauge

    def __ram(self):
        ram_gauge = GaugeMetricFamily(
            name="ram",
            documentation=f"Memory Statistics from Jetson Stats (unit: {self.jetson.jtop_stats['mem']['unit']}B)",
            labels=["statistic"],
            unit="kB"
        )
        ram_gauge.add_metric(["total"], value=self.jetson.jtop_stats["mem"]["tot"])
        ram_gauge.add_metric(["used"], value=self.jetson.jtop_stats["mem"]["use"])
        ram_gauge.add_metric(["shared"], value=self.jetson.jtop_stats["mem"]["shared"])
        return ram_gauge

    def __swap(self):
        swap_gauge = GaugeMetricFamily(
            name="swap",
            documentation=f"Swap Statistics from Jetson Stats (unit: {self.jetson.jtop_stats['swp']['unit']}B)",
            labels=["statistic"],
            unit="MB"
        )
        swap_gauge.add_metric(["total"], value=self.jetson.jtop_stats["swp"]["tot"])
        swap_gauge.add_metric(["used"], value=self.jetson.jtop_stats["swp"]["use"])
        swap_gauge.add_metric(["cached"], value=self.jetson.jtop_stats["swp"]["cached"]["size"])
        return swap_gauge

    def __temperature(self):
        temperature_gauge = GaugeMetricFamily(
            name="temperature",
            documentation=f"Temperature Statistics from Jetson Stats (unit: °C)",
            labels=["statistic", "machine_part", "operational_critical"],
            unit="C"
        )
        for part, temp in self.jetson.jtop_stats['tmp'].items():
            temperature_gauge.add_metric([part], value=temp)

        return temperature_gauge

    # def __voltage(self):
    #     voltage_gauge = GaugeMetricFamily(
    #         "voltage", "voltage statistics from tegrastats", labels=["source"],
    #     )
    #     for source, data in self.jetson.stats["VOLT"].items():
    #         voltage_gauge.add_metric([source], value=str(data["cur"]))
    #     return voltage_gauge

    def __disk(self):
        disk_gauge = GaugeMetricFamily(
            name="disk",
            documentation=f"Local Storage Statistics from Jetson Stats (unit: {self.jetson.disk_units})",
            labels=["mountpoint", "statistic"],
            unit="GB"
        )
        for mountpoint, disk_info in self.jetson.disk.items():
            if mountpoint == "/":
                disk_gauge.add_metric(["total"], value=disk_info["total"])
                disk_gauge.add_metric(["used"], value=disk_info["used"])
                disk_gauge.add_metric(["free"], value=disk_info["free"])
                disk_gauge.add_metric(["percent"], value=disk_info["percent"])

        return disk_gauge

    def __uptime(self):
        uptime_gauge = GaugeMetricFamily(
            name="uptime",
            documentation="Machine Uptime Statistics from Jetson Stats",
            labels=["statistic", "runtime"],
            unit="s"
        )
        uptime_gauge.add_metric(["alive"], value=self.jetson.jtop_stats["upt"].total_seconds())
        return uptime_gauge

    def collect(self):
        self.jetson.update()
        yield self.__cpu()
        yield self.__gpu()
        yield self.__ram()
        yield self.__iram()
        yield self.__swap()
        yield self.__temperature()
        yield self.__disk()
        yield self.__uptime()
