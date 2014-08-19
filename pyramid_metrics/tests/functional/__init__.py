import unittest
import time

import webtest

from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.httpexceptions import HTTPInternalServerError


def testview(request):
    request.metrics.incr("testcounter")

    with request.metrics.timer('contexttimer'):
        time.sleep(0.001)

    request.metrics.mark_start('marker')
    time.sleep(0.001)
    request.metrics.mark_stop('marker')

    request.metrics.timing('timing', 1)

    return Response('OK')


def testview_exc(request):
    raise HTTPInternalServerError(body_template='custom message')


def testview_context_exc(request):
    with request.metrics.timer('contexttimer'):
        raise Exception('exc-inside-contextmanager')


class TestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config = Configurator(settings={})
        cls.setUpMetrics(config)

        config.add_route(name='route_test', pattern='/1')
        config.add_view(testview, route_name='route_test')

        config.add_route(name='route_exc', pattern='/exc')
        config.add_view(testview_exc, route_name='route_exc')

        config.add_route(name='route_context_exc', pattern='/context_exc')
        config.add_view(testview_context_exc, route_name='route_context_exc')

        cls.wsgiapp = config.make_wsgi_app()

    def setUp(self):
        self.app = webtest.TestApp(self.wsgiapp)


class FunctionalTestBase(TestBase):
    @classmethod
    def setUpMetrics(cls, config):
        config.include('pyramid_metrics')
