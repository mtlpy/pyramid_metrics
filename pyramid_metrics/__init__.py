import os
import logging
import socket

log = logging.getLogger(__name__)


def includeme(config):
    settings = config.registry.settings

    host = 'localhost'
    host = settings.get('metrics.host', host)
    host = os.getenv('PYRAMID_METRICS_HOST', host)

    log.info('DNS resolution of %s...', host)
    settings['metrics.host'] = socket.gethostbyname(host)

    port = 8125
    port = settings.get('metrics.port', port)
    port = os.getenv('PYRAMID_METRICS_PORT', port)
    settings['metrics.port'] = int(port)

    config.include('.utility')
    config.include('.tween')
