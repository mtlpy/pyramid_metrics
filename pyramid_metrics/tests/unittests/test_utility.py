import unittest

import mock
from nose_parameterized import parameterized


class TestMetricsUtilityBase(unittest.TestCase):
    """ Base class for Utility test classes """

    def setUp(self):
        self.request = mock.Mock(name='request')
        self.request.registry.settings = {
            'metrics.host': 'metrics_host',
            'metrics.port': 1234,
            'metrics.prefix': 'metrics_prefix',
        }

    def get_metrics_utility(self):
        from pyramid_metrics.utility import MetricsUtility
        with mock.patch('pyramid_metrics.utility.StatsClient'):
            return MetricsUtility(self.request)


class TestMetricsUtility(TestMetricsUtilityBase):

    def test_init(self):
        from pyramid_metrics.utility import MetricsUtility
        with mock.patch('pyramid_metrics.utility.StatsClient') as m_client:
            mu = MetricsUtility(self.request)

        self.assertEqual(mu._statsd, m_client.return_value)
        self.assertEqual(mu.request, self.request)

    def test_request_method(self):
        from pyramid_metrics.utility import MetricsUtility
        with mock.patch('pyramid_metrics.utility.StatsClient'):
            mu = MetricsUtility.request_method(self.request)

        self.assertIsInstance(mu, MetricsUtility)

    def test_route_name(self):
        mu = self.get_metrics_utility()

        self.assertEqual(
            mu.route_name,
            self.request.matched_route.name.lower())

        self.request.matched_route = None
        self.assertEqual(mu.route_name, 'mock_mock')

    def test_route_key(self):
        mu = self.get_metrics_utility()

        self.assertEqual(
            mu._route_key('test'),
            'route.%s.test' % self.request.matched_route.name.lower())

    @parameterized.expand([
        ('key_str', 'member1.member2'),
        ('key_tuple', ('member1', 'member2')),
        ('key_list', ['member1', 'member2']),
    ])
    def test_key(self, name, stat):
        mu = self.get_metrics_utility()

        self.assertEqual(mu._key(stat), 'member1.member2')

    def test_incr(self):
        mu = self.get_metrics_utility()

        mu.incr(('incr', 'key'))
        mu._statsd.incr.assert_called_with('incr.key', count=1)

        mu._statsd.reset()
        mu.incr(('incr', 'key'), count=42)
        mu._statsd.incr.assert_called_with('incr.key', count=42)

    def test_incr_per_route(self):
        mu = self.get_metrics_utility()

        mu.incr(('incr', 'key'), per_route=True)
        mu._statsd.incr.assert_has_calls([
            mock.call('incr.key', count=1),
            mock.call('route.%s.incr.key' %
                self.request.matched_route.name.lower(), count=1),
        ])

    def test_timing(self):
        mu = self.get_metrics_utility()

        mu.timing(('timing', 'key'), 123)
        mu._statsd.timing.assert_called_with('timing.key', 123)

    def test_timing_per_route(self):
        mu = self.get_metrics_utility()

        mu.timing(('timing', 'key'), 123, per_route=True)
        mu._statsd.timing.assert_has_calls([
            mock.call('timing.key', 123),
            mock.call('route.%s.timing.key' %
                self.request.matched_route.name.lower(), 123),
        ])

    def test_mark_start(self):
        mu = self.get_metrics_utility()

        import time
        t_before = time.time()
        mu.mark_start('testkey')
        t_after = time.time()

        self.assertIn('testkey', mu.active_markers)
        self.assertTrue(t_before < mu.active_markers['testkey'].time < t_after)

    def test_mark_stop(self):
        mu = self.get_metrics_utility()

        import time
        t_before = time.time()
        mu.mark_start('testkey')
        t_after = time.time()

        time.sleep(0.1)

        t_interval_down = int((time.time() - t_after) * 1000)
        mu.mark_stop('testkey')
        t_interval_up = int((time.time() - t_before) * 1000)

        self.assertEqual(mu._statsd.timing.call_count, 2)

        key, dt = mu._statsd.timing.call_args_list[0][0]

        self.assertEqual(key, 'testkey')
        self.assertTrue(t_interval_down <= dt <= t_interval_up)

        key, dt = mu._statsd.timing.call_args_list[1][0]

        self.assertEqual(
            key,
            'route.%s.testkey' % mu.request.matched_route.name.lower())
        self.assertTrue(t_interval_down <= dt <= t_interval_up)

    def test_mark_stop_prefix(self):
        mu = self.get_metrics_utility()

        mu.mark_start('testkey')
        mu.mark_stop('testkey', prefix=('pre', 'fix'))

        key, dt = mu._statsd.timing.call_args_list[0][0]
        self.assertEqual(key, 'pre.fix.testkey')

    def test_mark_stop_suffix(self):
        mu = self.get_metrics_utility()

        mu.mark_start('testkey')
        mu.mark_stop('testkey', suffix=('suf', 'fix'))

        key, dt = mu._statsd.timing.call_args_list[0][0]
        self.assertEqual(key, 'testkey.suf.fix')


class TestMetricsUtilityFailsafe(TestMetricsUtilityBase):
    """ Separate tests to check the API doesn't throw exceptions """

    def test_route_name(self):
        mu = self.get_metrics_utility()

        self.request.matched_route = None
        del self.request.context
        mu.route_name

    def test_incr(self):
        mu = self.get_metrics_utility()

        mu.incr('test1')
        mu.incr('test2', per_route=False)
        mu.incr('test3', count=42)
        mu.incr('test4', per_route=True)
        mu.incr('test4', count=42, per_route=True)

    def test_timing(self):
        mu = self.get_metrics_utility()

        mu.timing('test1', 42)
        mu.timing('test1', 0)
        mu.timing('test1', -42)
        mu.timing('test2', 42, per_route=False)
        mu.timing('test4', 42, per_route=True)

    def test_marker(self):
        mu = self.get_metrics_utility()

        mu.mark_start('test1')
        mu.mark_start('test1')
        mu.mark_start('test2')

        mu.mark_stop('test1')
        mu.mark_stop('test2')
        mu.mark_stop('test2')
        mu.mark_stop('test3')

        mu.mark_stop('test2', prefix='')
        mu.mark_stop('test2', prefix='pretest')
        mu.mark_stop('test2', suffix='')
        mu.mark_stop('test2', suffix='pretest')

        mu.mark_stop('test3', per_route=True)

