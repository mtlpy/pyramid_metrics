import logging
import time

from pyramid.threadlocal import get_current_request
from statsd import StatsClient

log = logging.getLogger(__name__)


def includeme(config):
    settings = config.registry.settings

    host = settings['metrics.host']
    port = settings['metrics.port']

    log.info("Add metrics utility (sending to %s:%s)", host, port)

    config.add_request_method(MetricsUtility.request_method, 'metrics',
                              reify=True)


class MetricsError(Exception):
    pass


class MetricsUtilityUnavailable(MetricsError):
    pass


def get_current_metrics():
    request = get_current_request()
    if request is None:
        raise MetricsUtilityUnavailable("No active pyramid request")
    return request.metrics


class Marker(object):
    def __init__(self, name, count=True, timing=True):
        self.name = name
        self.time = time.time()

    def get_delta_from(self, other):
        """ return deltatime in millisecond """
        return int((self.time - other.time) * 1000)


class MetricsUtility(object):
    """ Pyramid utility for light metrology. Available as a request method.
    """

    def __init__(self, request):
        self.request = request

        self._statsd = StatsClient(
            host=request.registry.settings['metrics.host'],
            port=request.registry.settings['metrics.port'],
            prefix=request.registry.settings.get('metrics.prefix'))

        self.active_markers = {}

    @classmethod
    def request_method(cls, request):
        return cls(request)

    @property
    def route_name(self):
        """ Get a route name from URL Dispatch or Traversal """
        if self.request.matched_route:
            route_name = self.request.matched_route.name
        else:
            try:
                ctx_class = self.request.context.__class__
            except AttributeError:
                return 'unkown'
            ctx_name = ctx_class.__name__
            ctx_module = ctx_class.__module__.rsplit('.', 1)[-1]
            route_name = '%s_%s' % (ctx_module, ctx_name)
        return route_name.lower()

    def _route_key(self, stat):
        return 'route.%s.%s' % (self.route_name, stat)

    def _key(self, stat):
        if isinstance(stat, (list, tuple)):
            return '.'.join([str(member) for member in stat])
        else:
            return str(stat)

    def incr(self, stat, count=1, per_route=False):
        """ Push a COUNTER metric

        >>> request.metrics.incr('mysql.reconnection')
        >>> request.metrics.incr(['mysql', 'reconnection'])
        """
        self._statsd.incr(self._key(stat), count=count)
        if per_route:
            self._statsd.incr(self._route_key(self._key(stat)),
                              count=count)

    def timing(self, stat, dt, per_route=False):
        """ Push a TIMER metric (in milliseconds)

        >>> start_time = time()
        >>> ...
        >>> request.metrics.timing('mysql.select', time() - start_time)
        >>> request.metrics.timing(['mysql', 'select'], time() - start_time)
        """
        self._statsd.timing(self._key(stat), dt)
        if per_route:
            self._statsd.timing(self._route_key(self._key(stat)), dt)

    def mark_start(self, marker_name):
        """ Place a start time marker.

        >>> request.metrics.mark_start('longprocess')
        >>> ...
        >>> request.metrics.mark_stop('longprocess')
        """
        start_marker = Marker(marker_name)
        self.active_markers[marker_name] = start_marker

    def mark_stop(self, marker_name, prefix='', suffix='', per_route=True):
        """ Place a stop time marker. Effectively pushing an TIMER from a
            start marker

        >>> try:
        >>>     response = metrics.mark_start('longprocess')
        >>>     ...
        >>> except:
        >>>     metrics.mark_stop('longprocess', prefix='exc')
        >>> else:
        >>>     if response.condition:
        >>>         metrics.mark_stop('longprocess', prefix=response.outcome)
        >>>     else:
        >>>         metrics.mark_stop('longprocess')
        """
        stop_marker = Marker(marker_name)
        start_marker = self.active_markers.get(marker_name)

        if start_marker:
            stat = [marker_name]
            if prefix:
                stat.insert(0, self._key(prefix))
            if suffix:
                stat.append(self._key(suffix))
            dt = stop_marker.get_delta_from(start_marker)

            self.timing(stat, dt=dt, per_route=per_route)
