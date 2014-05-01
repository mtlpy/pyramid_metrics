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
        from pyramid_metrics import performance_tween_factory

        performance_tween_factory(self.handler, self.registry)


    def test_tween_factory_name(self):
        from pyramid_metrics import performance_tween_factory

        tween = performance_tween_factory(self.handler, self.registry)

        self.assertEqual(tween.__name__, 'performance_tween')

