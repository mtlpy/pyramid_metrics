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
        http_method = request.method.lower()
        try:
            request.metrics.mark_start('request')
            response = handler(request)
        except:
            request.metrics.mark_stop('request', suffix=(http_method, 'exc'))
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

            request.metrics.mark_stop(
                'request', suffix=(http_method, status_code))
            # request.metrics.mark_stop(
            #     'request', suffix=(http_method, 'total'))

            return response

    return performance_tween
