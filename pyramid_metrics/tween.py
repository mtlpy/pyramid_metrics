from time import time
import logging

from pyramid.settings import asbool

log = logging.getLogger(__name__)


def includeme(config):
    settings = config.registry.settings

    if asbool(settings.get('metrics.route_performance', True)):
        log.info('Add route metrics tween')
        config.add_tween('pyramid_metrics.tween.performance_tween_factory')


def performance_tween_factory(handler, registry):

    def performance_tween(request):
        start = time()
        stat = ['request', request.method.lower()]

        try:
            response = handler(request)
        except:
            dt = time() - start
            request.metrics.timing(stat + ['exc'], dt=dt, per_route=True)
            raise

        else:
            if 200 <= response.status_code < 300:
                status_code = '2xx'
            elif 300 <= response.status_code < 400:
                status_code = '3xx'
            elif 400 <= response.status_code < 500:
                status_code = '4xx'
            elif 500 <= response.status_code < 600:
                status_code = '5xx'
            else:
                status_code = 'xxx'

            dt = time() - start
            request.metrics.timing(stat + [status_code], dt=dt, per_route=True)

            return response

    return performance_tween
