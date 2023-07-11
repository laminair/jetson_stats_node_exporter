# Nvidia Jetson Prometheus Node Exporter (incl. GPU) - no including AGX Orin platform

This project contains a node exporter variation building on jetson-stats (jtop) rather than tegrastats directly.
We export the following metrics: 
- CPU
- Memory 
- GPU 
- VRAM
- Swap
- Component Temperature
- Disk Utilization
- System Uptime

We do not export: 
- Power consumption

## Installation
You can either clone this repo or use pip for installation. 
Wheels or binaries are provided here: [Jetson Stats Node Exporter Releases](https://github.com/laminair/jetson_stats_node_exporter/releases)

Installation with pip (no venv or conda due to jetson-stats dependency!): 
```
> export JSN_RELEASE="0.0.3"
> sudo -H pip3 install -U https://github.com/laminair/jetson_stats_node_exporter/releases/download/$JSN_RELEASE/jetson_stats_node_exporter-$JSN_RELEASE-py3-none-any.whl
```

Manual installation (may require sudo privileges due to jetson-stats dependency): 
```
> git clone https://github.com/laminair/jetson_stats_node_exporter.git
> cd jetson_stats_node_exporter
> python3 setup.py install
```

## Running the exporter
After installation the project is available as python module. Run it as follows:
```
python3 -m jetson_node_exporter
```

This will spawn a prometheus node exporter service on port 9100 and you'll be able to scrape all statistics.
Note: The command above can also be run as a systemd service in the background.

## Credits
This project is based on https://github.com/lipovsek/jetson_prometheus_exporter, which uses tegrastats.