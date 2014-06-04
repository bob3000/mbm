import unittest
import mbm.lib.oauth

from unittest.mock import MagicMock


class ApiTestCase(unittest.TestCase):

    def test_authorize_request(self):
        request = MagicMock()
        request.full_url = "http://github.com?a=b&c=d"
        request.get_method = lambda: "POST"
        auth = mbm.lib.oauth.OAuth("consumer_key",
                                   "consumer_secret",
                                   "token",
                                   "token_secret")
        auth.authorize_request(request)
        expected_calls = []  # TODO
        self.assertEquals(expected_calls, request.mock_calls)
