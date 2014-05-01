import os
import logging
import socket

from pyramid.settings import asbool

from pyramid_metrics.utility import MetricsUtility

log = logging.getLogger(__name__)


def includeme(config):
    settings = config.registry.settings

    host = 'localhost'
    host = settings.get('metrics.host', host)
    host = os.getenv('PYRAMID_METRICS_HOST', host)

    log.info("DNS resolution of %s...", host)
    settings['metrics.host'] = socket.gethostbyname(host)

    port = 8125
    port = settings.get('metrics.port', port)
    port = os.getenv('PYRAMID_METRICS_PORT', port)
    settings['metrics.port'] = int(port)

    log.info("Add metrics utility (sending to %s:%s)", host, port)
    config.add_request_method(MetricsUtility.request_method,
                              'metrics',
                              reify=True)

    if asbool(settings.get('metrics.route_performance', True)):
        log.info("Add route metrics tween")
        config.add_tween('.performance_tween_factory')


def performance_tween_factory(handler, registry):

    def performance_tween(request):
        try:
            request.metrics.mark_start('request')
            response = handler(request)
        except:
            request.metrics.mark_stop('request', suffix='.exc')
            raise

        else:
            if 200 <= response.status_code < 300:
                suffix = '.2xx'
            elif 300 <= response.status_code < 400:
                suffix = '.3xx'
            elif 400 <= response.status_code < 500:
                suffix = '.4xx'
            elif 500 <= response.status_code < 600:
                suffix = '.5xx'
            else:
                suffix = '.xxx'
            request.metrics.mark_stop('request', suffix=suffix)

            return response

    return performance_tween
