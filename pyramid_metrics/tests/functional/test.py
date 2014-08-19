import mock

from pyramid_metrics.tests.functional import FunctionalTestBase


@mock.patch('pyramid_metrics.utility.StatsClient')
class Test(FunctionalTestBase):

    def test_get(self, client):
        self.app.get('/1')

        client.return_value.incr.assert_called_once_with(
            'testcounter', count=1)

        client.return_value.timing.assert_has_calls([
            mock.call('contexttimer', mock.ANY),

            mock.call('marker', mock.ANY),
            mock.call('route.route_test.marker', mock.ANY),

            mock.call('timing', 1000),

            mock.call('request.get.2xx', mock.ANY),
            mock.call('route.route_test.request.get.2xx', mock.ANY),
            ])

    def test_unkown_route(self, client):
        self.app.get('/unkown', status=404)

        client.return_value.timing.assert_has_calls([
            mock.call('request.get.4xx', mock.ANY),
            mock.call('route.traversal_defaultrootfactory.request.get.4xx', mock.ANY),
            ])

    def test_exc_route(self, client):
        response = self.app.get('/exc', status=500)
        self.assertEqual(response.text,
                         '500 Internal Server Error\n\ncustom message')

        client.return_value.timing.assert_has_calls([
            mock.call('request.get.5xx', mock.ANY),
            mock.call('route.route_exc.request.get.5xx', mock.ANY),
            ])
