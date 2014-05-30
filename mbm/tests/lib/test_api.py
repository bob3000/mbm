import unittest
import urllib.request
import mbm.lib.api

from unittest.mock import MagicMock


class ApiTestCase(unittest.TestCase):

    def setUp(self):
        self.request = urllib.request
        urllib.request = MagicMock()

    def test_api_call(self):
        api = mbm.lib.api.Api(url_prefix="http://some.url")
        api.posts_queue(api_key="asdf98", some="value")
        urllib.request.urlopen.assert_called_with(
            "http://some.url/posts/queue?api_key=asdf98&some=value")

        api.posts(api_key="asdf98",
                  post_data={"type": "text", "title": "My new bike"})
        urllib.request.urlopen.assert_called_with(
            "http://some.url/posts?api_key=asdf98",
            data={"type": "text", "title": "My new bike"})

    def tearDown(self):
        urllib.request = self.request
