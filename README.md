# Nvidia Jetson Nano Prometheus Node Exporter (incl. GPU)

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


## Credits
This project is based on https://github.com/lipovsek/jetson_prometheus_exporter, which uses tegrastats.