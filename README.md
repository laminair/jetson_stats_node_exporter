# Nvidia Jetson Prometheus Node Exporter (incl. GPU) - incl. JetPack 6.0

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
Make sure your local installation of jetson-stats is 4.2.9. Otherwise, you will run into dependency issues.
```
pip install jetson-stats-node-exporter==0.1.1
```

### Install from git

Installation with pip (no venv or conda due to jetson-stats dependency!): 
```
> export JSN_RELEASE="0.1.1"
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
python3 -m jetson_stats_node_exporter
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

### Creating a docker image
The node exporter can be wrapped in a docker image and can be run via docker.
If you use docker compose you can build the image directly via docker compose.
Place the Dockerfile in the same directory as your docker-compose.yaml, 
or use the context option in your docker-compose.yaml to specify the folder containing the Dockerfile.
```
  jetson_stats_node_exporter:
    build:
      context: <PATH_TO_JETSON_STATS_NODE_EXPORTER_PACKAGE>
      dockerfile: Dockerfile
    container_name: jetson_stats_node_exporter
    restart: always
    ports:
      - "9100:9100"  # Map internal port 9100 to a different external port 9100
    volumes:
      - /run/jtop.sock:/run/jtop.sock
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:9100/metrics"]
      interval: 30s
      timeout: 10s
      retries: 10
      start_period: 60s
```

**Important Note:** 
When using docker, you may not be able to export disk statistics. 
Please see [this GitHub issue](https://github.com/laminair/jetson_stats_node_exporter/issues/7).

## Credits
This project is based on https://github.com/lipovsek/jetson_prometheus_exporter, which uses tegrastats.
