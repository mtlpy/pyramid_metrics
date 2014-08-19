from pyramid_metrics.tests.functional import FunctionalTestBase


class TestFailsafe(FunctionalTestBase):

    def test_get(self):
        self.app.get('/1')

    def test_unkown_route(self):
        self.app.get('/definitely-unnkown', status=404)

    def test_context_exc(self):
        with self.assertRaises(Exception):
            self.app.get('/context_exc')

    def test_exc(self):
        response = self.app.get('/exc', status=500)
        self.assertEqual(response.text,
                         '500 Internal Server Error\n\ncustom message')

