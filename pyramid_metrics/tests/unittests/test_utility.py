import unittest

import mock
from nose_parameterized import parameterized

from pyramid import testing


class TestMetricsUtilityBase(unittest.TestCase):
    """ Base class for Utility test classes """

    def get_metrics_utility(self):
        from pyramid_metrics.utility import MetricsUtility
        mock_statsd = mock.Mock(name='MockStatsdClient')
        return MetricsUtility(statsd=mock_statsd, route_name='route_name')


class TestMetricsUtility(TestMetricsUtilityBase):
    def setUp(self):
        self.mu = self.get_metrics_utility()

    def test_request_method(self):
        m_request = mock.Mock(name='request')
        m_request.registry.settings = {
            'metrics.host': 'metrics_host',
            'metrics.port': 1234,
            'metrics.prefix': 'metrics_prefix',
        }
        from pyramid_metrics.utility import get_request_method
        with mock.patch('pyramid_metrics.utility.StatsClient') as m_client:
            mu = get_request_method(m_request)

        self.assertEqual(mu._statsd, m_client.return_value)

    def test_route_name(self):
        mu = self.get_metrics_utility()

        self.assertEqual(
            mu.route_name,
            'route_name')

    def test_route_key(self):
        mu = self.get_metrics_utility()

        self.assertEqual(
            mu._route_key('test'),
            'route.route_name.test')

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
            mock.call('route.route_name.incr.key', count=1),
        ])

    def test_timing(self):
        mu = self.get_metrics_utility()

        mu.timing(('timing', 'key'), 0.123)
        mu._statsd.timing.assert_called_with('timing.key', 123)

    def test_timing_per_route(self):
        mu = self.get_metrics_utility()

        mu.timing(('timing', 'key'), 0.123, per_route=True)
        mu._statsd.timing.assert_has_calls([
            mock.call('timing.key', 123),
            mock.call('route.route_name.timing.key', 123),
        ])

    def test_timer(self):
        import time

        t_interval_down = 0.001

        t_before = time.time()
        with self.mu.timer('context'):
            time.sleep(t_interval_down)
        t_interval_up = int((time.time() - t_before) * 1000)

        self.assertEqual(self.mu._statsd.timing.call_count, 1)

        key, dt = self.mu._statsd.timing.call_args_list[0][0]

        self.assertEqual(key, 'context')
        self.assertTrue(t_interval_down <= dt <= t_interval_up)

    def test_timer_exception(self):
        class TestExc(Exception): pass

        with self.assertRaises(TestExc):
            with self.mu.timer('context'):
                raise TestExc()

        self.assertEqual(self.mu._statsd.timing.call_count, 1)
        key, _ = self.mu._statsd.timing.call_args_list[0][0]
        self.assertEqual(key, 'context.exc')

    def test_mark_start(self):
        mu = self.get_metrics_utility()

        import time
        t_before = time.time()
        mu.mark_start('testkey')
        t_after = time.time()

        self.assertIn('testkey', mu.active_markers)
        self.assertTrue(t_before <= mu.active_markers['testkey'].time <= t_after)

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
            'route.route_name.testkey')
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


class TestMetricsUtilityCurrent(unittest.TestCase):
    def tearDown(self):
        testing.tearDown()

    def test_current_utility(self):
        from pyramid_metrics.utility import get_current_metrics

        request = mock.Mock()
        testing.setUp(request=request)

        metrics = get_current_metrics()
        self.assertEqual(metrics, request.metrics)


    def test_current_utility_no_request(self):
        from pyramid_metrics.utility import (
            get_current_metrics,
            MetricsUtilityUnavailable,
            )

        testing.setUp(request=None)

        with self.assertRaises(MetricsUtilityUnavailable):
            get_current_metrics()
