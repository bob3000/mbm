import unittest
import gzip
import urllib.request
import mbm.lib.api
import mbm.lib.oauth

from unittest.mock import MagicMock


class ApiTestCase(unittest.TestCase):

    def setUp(self):
        self.request = urllib.request

        self.http_response = MagicMock()
        self.http_response.getheaders = \
            lambda: [("content-type", "application/json")]
        self.http_response.read = \
            lambda: gzip.compress(b'{"content": "my content"}')

        attrs = {'urlopen.return_value': self.http_response}
        urllib.request = MagicMock()
        urllib.request.configure_mock(**attrs)

        self.request_Request = urllib.request.Request
        urllib.request.Request = MagicMock()

        self.oauth = MagicMock()
        self.oauth.authorize_request = lambda x, exclude_params=False: x

    def test_api_call(self):
        api = mbm.lib.api.Api(self.oauth, "http://some.url")
        api.posts.queue(params={'api_key': 'asdf98', 'some': 'value'})
        urllib.request.Request.assert_called_with(
            'http://some.url/posts/queue?api_key=asdf98&some=value',
            method='GET', headers={})

    def test_api_call_with_payload(self):
        api = mbm.lib.api.Api(self.oauth, "http://some.url")
        api.posts(params={'api_key': 'asdf98'},
                  post_data='{"type": "text", "title": "My new bike"}')
        urllib.request.Request.assert_called_with(
            'http://some.url/posts?api_key=asdf98',
            data=b'{"type": "text", "title": "My new bike"}',
            headers={}, method='POST')

    def test_wrong_content_type(self):
        api = mbm.lib.api.Api(self.oauth, "http://some.url")
        self.http_response.getheaders = \
            lambda: [("content-type", "text/html")]
        attrs = {'urlopen.return_value': self.http_response}
        urllib.request.configure_mock(**attrs)
        with self.assertRaises(mbm.lib.api.ApiException):
            api.posts_queue(params={'api_key': 'asdf98', 'some': 'value'})

    def test_wrong_payload(self):
        api = mbm.lib.api.Api(self.oauth, "http://some.url")
        self.http_response.read = lambda: b'<html></html>'
        attrs = {'urlopen.return_value': self.http_response}
        urllib.request.configure_mock(**attrs)
        with self.assertRaises(mbm.lib.api.ApiException):
            api.posts_queue(params={'api_key': 'asdf98', 'some': 'value'})

    def test_http_error(self):
        api = mbm.lib.api.Api(self.oauth, "http://some.url")
        attrs = {'urlopen.side_effect': mbm.lib.oauth.OAuthException}
        urllib.request.configure_mock(**attrs)
        with self.assertRaises(mbm.lib.api.ApiException):
            api.posts_queue(params={'api_key': 'asdf98', 'some': 'value'})

    def tearDown(self):
        urllib.request = self.request
        urllib.request.Request = self.request_Request
