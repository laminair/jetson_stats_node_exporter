from prometheus_client.core import GaugeMetricFamily
from .logger import factory
from .jtop_stats import JtopObservable


class Jetson(object):
    def __init__(self, update_period=1):

        if float(update_period) < 0.5:
            raise BlockingIOError("Jetson Stats only works with 0.5s monitoring intervals and slower.")

        self.jtop_observer = JtopObservable(update_period=update_period)
        self.jtop_stats = {}
        self.disk = {}
        self.disk_units = "GB"
        self.interval = update_period

    def update(self):
        self.jtop_stats = self.jtop_observer.read_stats()
        self.disk, self.disk_units = self.jtop_observer.get_storage_info()


class JetsonExporter(object):

    def __init__(self, update_period):
        self.jetson = Jetson(update_period)
        self.logger = factory(__name__)
        self.name = "Jetson"

    def __cpu(self):
        cpu_gauge = GaugeMetricFamily(
            name="cpu",
            documentation="CPU Statistics from Jetson Stats (ARMv8 Processor rev 1 (v8l))",
            labels=["core", "statistic"],
            unit="Hz"
        )

        for core_number, core_data in enumerate(self.jetson.jtop_stats["cpu"]["cpu"]):
            cpu_gauge.add_metric([str(core_number), "freq"], value=core_data["freq"]["cur"])
            cpu_gauge.add_metric([str(core_number), "min_freq"], value=core_data["freq"]["min"])
            cpu_gauge.add_metric([str(core_number), "max_freq"], value=core_data["freq"]["max"])
            cpu_gauge.add_metric([str(core_number), "val"], value=core_data["idle"])
        return cpu_gauge

    def __gpu(self):
        gpu_gauge = GaugeMetricFamily(
            name="gpu_utilization_percentage",
            documentation="GPU Statistics from Jetson Stats",
            labels=["statistic", "nvidia_gpu"],
            unit="Hz"
        )

        gpu_names = self.jetson.jtop_stats["gpu"].keys()

        for gpu_name in gpu_names:
            gpu_gauge.add_metric([gpu_name, "freq"], value=self.jetson.jtop_stats["gpu"][gpu_name]["freq"]["cur"])
            gpu_gauge.add_metric([gpu_name, "min_freq"], value=self.jetson.jtop_stats["gpu"][gpu_name]["freq"]["min"])
            gpu_gauge.add_metric([gpu_name, "max_freq"], value=self.jetson.jtop_stats["gpu"][gpu_name]["freq"]["max"])

        return gpu_gauge

    def __gpuram(self):
        gpuram_gauge = GaugeMetricFamily(
            name="gpuram",
            documentation=f"Video Memory Statistics from Jetson Stats",
            labels=["statistic", "nvidia_gpu"],
            unit="kB"
        )

        gpu_names = self.jetson.jtop_stats["gpu"].keys()

        for gpu_name in gpu_names:
            gpuram_gauge.add_metric([gpu_name, "mem"], value=self.jetson.jtop_stats["mem"]["RAM"]["shared"])

        return gpuram_gauge

    def __ram(self):
        ram_gauge = GaugeMetricFamily(
            name="ram",
            documentation=f"Memory Statistics from Jetson Stats (unit: kB)",
            labels=["statistic"],
            unit="kB"
        )

        ram_gauge.add_metric(["total"], value=self.jetson.jtop_stats["mem"]["RAM"]["tot"])
        ram_gauge.add_metric(["used"], value=self.jetson.jtop_stats["mem"]["RAM"]["used"])
        ram_gauge.add_metric(["buffers"], value=self.jetson.jtop_stats["mem"]["RAM"]["buffers"])
        ram_gauge.add_metric(["cached"], value=self.jetson.jtop_stats["mem"]["RAM"]["cached"])
        ram_gauge.add_metric(["lfb"], value=self.jetson.jtop_stats["mem"]["RAM"]["lfb"])
        ram_gauge.add_metric(["free"], value=self.jetson.jtop_stats["mem"]["RAM"]["free"])

        return ram_gauge

    def __swap(self):
        swap_gauge = GaugeMetricFamily(
            name="swap",
            documentation=f"Swap Statistics from Jetson Stats",
            labels=["statistic"],
            unit="kB"
        )

        swap_gauge.add_metric(["total"], value=self.jetson.jtop_stats["mem"]["SWAP"]["tot"])
        swap_gauge.add_metric(["used"], value=self.jetson.jtop_stats["mem"]["SWAP"]["used"])
        swap_gauge.add_metric(["cached"], value=self.jetson.jtop_stats["mem"]["SWAP"]["cached"])

        return swap_gauge

    def __emc(self):
        emc_gauge = GaugeMetricFamily(
            name="emc",
            documentation=f"EMC Statistics from Jetson Stats",
            labels=["statistic"],
            unit="Hz"
        )

        emc_gauge.add_metric(["total"], value=self.jetson.jtop_stats["mem"]["EMC"]["cur"])
        emc_gauge.add_metric(["used"], value=self.jetson.jtop_stats["mem"]["EMC"]["max"])
        emc_gauge.add_metric(["cached"], value=self.jetson.jtop_stats["mem"]["EMC"]["min"])

        return emc_gauge

    def __temperature(self):
        temperature_gauge = GaugeMetricFamily(
            name="temperature",
            documentation=f"Temperature Statistics from Jetson Stats (unit: °C)",
            labels=["statistic", "machine_part", "system_critical"],
            unit="C"
        )
        for part, temp in self.jetson.jtop_stats['tmp'].items():
            temperature_gauge.add_metric([part], value=temp["temp"])

        return temperature_gauge

    def __integrated_power_machine_parts(self):
        power_gauge = GaugeMetricFamily(
            name="integrated_power",
            documentation="Power Statistics from internal power sensors (unit: mW/V/A)",
            labels=["statistic", "machine_part", "system_critical"]
        )

        for part, reading in self.jetson.jtop_stats["pwr"]["rail"].items():
            power_gauge.add_metric(["voltage"], value=reading["volt"])
            power_gauge.add_metric(["current"], value=reading["curr"])
            power_gauge.add_metric(["critical"], value=reading["warn"])
            power_gauge.add_metric(["power"], value=reading["power"])
            power_gauge.add_metric(["avg_power"], value=reading["avg"])

        return power_gauge

    def __integrated_power_total(self):
        power_gauge = GaugeMetricFamily(
            name="integrated_power",
            documentation="Power Statistics from internal power sensors (unit: mW)",
            labels=["statistic", "machine_part", "system_critical"],
            unit="mW"
        )

        power_gauge.add_metric(["power"], value=self.jetson.jtop_stats["pwr"]["tot"]["power"])
        power_gauge.add_metric(["avg_power"], value=self.jetson.jtop_stats["pwr"]["tot"]["avg"])

        return power_gauge

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
        yield self.__gpuram()
        yield self.__swap()
        yield self.__emc()
        yield self.__temperature()
        yield self.__integrated_power_machine_parts()
        yield self.__integrated_power_total()
        yield self.__disk()
        yield self.__uptime()
