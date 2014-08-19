import unittest

import mock
from nose_parameterized import parameterized

from pyramid import testing


class TestMetricsTweenFactory(unittest.TestCase):

    def setUp(self):
        self.config = testing.setUp()
        self.registry = self.config.registry
        self.handler = mock.Mock(name='handler')

    def test_tween_factory(self):
        from pyramid_metrics.tween import performance_tween_factory

        performance_tween_factory(self.handler, self.registry)

    def test_tween_factory_name(self):
        from pyramid_metrics.tween import performance_tween_factory

        tween = performance_tween_factory(self.handler, self.registry)

        self.assertEqual(tween.__name__, 'performance_tween')


class TestMetricsTweenSafety(unittest.TestCase):
    """Safety check. This tween shouldn't change the outcome of the response"""

    def setUp(self):
        self.response = mock.Mock(name='response')
        self.handler = mock.Mock(name='handler', return_value=self.response)
        self.request = mock.Mock(name='request')
        self.request.metrics = mock.Mock(name='MetricsUtility')

        from pyramid_metrics.tween import performance_tween_factory
        self.tween = performance_tween_factory(self.handler, None)

    def _call(self):
        return self.tween(self.request)

    def test_handler(self):
        self._call()
        self.handler.assert_called_once_with(self.request)

    def test_exception(self):
        class test_exc(Exception):
            pass
        self.handler.side_effect = test_exc()

        with self.assertRaises(test_exc):
            self._call()

    def test_response(self):
        self.assertEqual(self._call(), self.handler.return_value)


class TestMetricsTween(unittest.TestCase):
    """Check metrics collection"""

    def setUp(self):
        self.response = mock.Mock(name='response')
        self.handler = mock.Mock(name='handler', return_value=self.response)
        self.request = mock.Mock(name='request')
        self.request.metrics = mock.Mock(name='MetricsUtility')

        from pyramid_metrics.tween import performance_tween_factory
        self.tween = performance_tween_factory(self.handler, None)

    def _call(self):
        return self.tween(self.request)

    @parameterized.expand([
        ('status_OK', 200, '2xx'),
        ('status_REDIRECT', 300, '3xx'),
        ('status_CLIENTERROR', 400, '4xx'),
        ('status_SERVERERROR', 500, '5xx'),
    ])
    def test_ok(self, name, status, suffix):
        self.response.status_code = status
        with mock.patch('pyramid_metrics.tween.time') as m_time:
            m_time.side_effect = [1, 2]
            self._call()

        self.request.metrics.timing.assert_called_once_with(
            ['request', self.request.method.lower(), suffix],
            dt=1,
            per_route=True)

    def test_exception(self):
        class test_exc(Exception):
            pass
        self.handler.side_effect = test_exc()

        with mock.patch('pyramid_metrics.tween.time') as m_time:
            m_time.side_effect = [1, 2]
            with self.assertRaises(test_exc):
                self._call()

        self.request.metrics.timing.assert_called_once_with(
            ['request', self.request.method.lower(), 'exc'],
            dt=1,
            per_route=True)
