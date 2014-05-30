import unittest
import urllib.request
import mbm.lib.api

from unittest.mock import MagicMock


class ApiTestCase(unittest.TestCase):

    def setUp(self):
        self.request = urllib.request

        self.http_response = MagicMock()
        self.http_response.getheaders = \
            lambda: [("content-type", "application/json")]
        self.http_response.read = lambda: '{"content": "my content"}'

        attrs = {'urlopen.return_value': self.http_response}
        urllib.request = MagicMock()
        urllib.request.configure_mock(**attrs)

    def test_api_call(self):
        api = mbm.lib.api.Api(url_prefix="http://some.url")
        api.posts_queue(api_key="asdf98", some="value")
        urllib.request.urlopen.assert_called_with(
            "http://some.url/posts/queue?api_key=asdf98&some=value")

    def test_api_call_with_payload(self):
        api = mbm.lib.api.Api(url_prefix="http://some.url")
        api.posts(api_key="asdf98",
                  post_data={"type": "text", "title": "My new bike"})
        urllib.request.urlopen.assert_called_with(
            "http://some.url/posts?api_key=asdf98",
            data={"type": "text", "title": "My new bike"})

    def test_wrong_content_type(self):
        api = mbm.lib.api.Api(url_prefix="http://some.url")
        self.http_response.getheaders = \
            lambda: [("content-type", "text/html")]
        attrs = {'urlopen.return_value': self.http_response}
        urllib.request.configure_mock(**attrs)
        with self.assertRaises(mbm.lib.api.ApiException):
            api.posts_queue(api_key="asdf98", some="value")

    def test_wrong_payload(self):
        api = mbm.lib.api.Api(url_prefix="http://some.url")
        self.http_response.read = lambda: '<html></html>'
        attrs = {'urlopen.return_value': self.http_response}
        urllib.request.configure_mock(**attrs)
        with self.assertRaises(mbm.lib.api.ApiException):
            api.posts_queue(api_key="asdf98", some="value")

    def tearDown(self):
        urllib.request = self.request
