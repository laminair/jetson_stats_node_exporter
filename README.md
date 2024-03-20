# Nvidia Jetson Prometheus Node Exporter (incl. GPU) - now including AGX Orin platform with JetPack 6.0

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

### Easy Installation via PyPi

```
pip install jetson-stats-node-exporter==0.0.6
```

### Install from git

Installation with pip (no venv or conda due to jetson-stats dependency!): 
```
> export JSN_RELEASE="0.0.6"
> sudo -H pip3 install -U https://github.com/laminair/jetson_stats_node_exporter/releases/download/$JSN_RELEASE/jetson_stats_node_exporter-$JSN_RELEASE-py3-none-any.whl
```

### Install from source
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

### Creating a background service
The node exporter can be wrapped in a systemd service.
Place the following file in path `/etc/systemd/system/jetson-stats-node-exporter.service`

```
[Unit]
Description=Jetson Stats GPU Node Exporter
After=multi-user.target
Requires=jtop.service

[Service]
Type=simple
Restart=on-failure
RestartSec=10
User=root
Group=root
ExecStart=/usr/bin/python3 -m jetson_stats_node_exporter

[Install]
WantedBy=multi-user.target
```

Then run `sudo systemctl start jetson-stats-node-exporter`. 
To check if the service is alive `sudo systemctl status jetson-stats-node-exporter`

## Credits
This project is based on https://github.com/lipovsek/jetson_prometheus_exporter, which uses tegrastats.
