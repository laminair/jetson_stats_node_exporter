from time import sleep
import argparse

from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY
import schedule

from .exporter import JetsonExporter
from .logger import factory


def start_exporter(port=9100, update_period=1, logfile_cleanup_interval_hours=24):
    logger = factory(__name__)
    logger.info(f"Node exporter running on port {port}. Querying speed: {update_period}s. "
                f"Cleanup frequency: {logfile_cleanup_interval_hours}")
    start_http_server(port)
    data_collector = JetsonExporter(update_period)

    sleep(update_period * 2)
    REGISTRY.register(data_collector)
    while True:
        schedule.run_pending()
        sleep(100)


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, nargs='?', default=9100, help='Node exporter port')
    parser.add_argument('--update_period', type=int, nargs='?', default=1, help='Querying speed.')
    parser.add_argument('--logfile_cleanup_interval_hours', type=int, nargs='?', default=24,
                        help='Local log cleanup frequency.')
    return vars(parser.parse_args())


if __name__ == '__main__':
    start_exporter(**cli())
