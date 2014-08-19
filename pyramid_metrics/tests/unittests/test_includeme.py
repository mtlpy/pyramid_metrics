import unittest

import mock
from nose_parameterized import parameterized


class TestMetricsInclude(unittest.TestCase):

    @mock.patch('pyramid_metrics.utility.MetricsUtility')
    def test_includeme(self, m_utility):
        from pyramid_metrics import includeme as include0
        from pyramid_metrics.utility import includeme as include1
        from pyramid_metrics.utility import get_request_method
        from pyramid_metrics.tween import includeme as include2

        config = mock.Mock()
        config.registry.settings = {}

        with mock.patch('socket.gethostbyname'):
            include0(config)
            include1(config)
            include2(config)

        config.add_request_method.assert_called_once_with(
            get_request_method,
            'metrics',
            reify=True)

        config.add_tween.assert_called_once_with(
            'pyramid_metrics.tween.performance_tween_factory')

    @parameterized.expand([
        ('empty',
         {},
         {'metrics.host': '127.0.1.1', 'metrics.port': 8125}),
        ('localhost',
         {'metrics.host': 'localhost'},
         {'metrics.host': '127.0.1.1', 'metrics.port': 8125}),
        ('example.com',
         {'metrics.host': 'example.com'},
         {'metrics.host': '127.0.1.1', 'metrics.port': 8125}),
        ('port',
         {'metrics.port': '1111'},
         {'metrics.host': '127.0.1.1', 'metrics.port': 1111})
    ])
    @mock.patch('pyramid_metrics.utility.MetricsUtility')
    def test_includeme_params(self, name, settings, expected, m_utility):
        from pyramid_metrics import includeme

        config = mock.Mock()
        config.registry.settings = settings

        with mock.patch('socket.gethostbyname') as ghbn:
            expected_host = settings.get('metrics.host', 'localhost')
            ghbn.return_value = '127.0.1.1'
            includeme(config)
            ghbn.assert_called_once_with(expected_host)

        self.assertEqual(config.registry.settings, expected)

    @mock.patch('pyramid_metrics.utility.MetricsUtility')
    def test_includeme_tween_disabled(self, m_utility):
        from pyramid_metrics import includeme

        config = mock.Mock()
        config.registry.settings = {'metrics.route_performance': 'false'}

        with mock.patch('socket.gethostbyname'):
            includeme(config)

        self.assertEqual(config.add_tween.call_count, 0)
