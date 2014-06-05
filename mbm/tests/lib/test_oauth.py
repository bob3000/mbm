import time
import unittest
import mbm.lib.oauth

from unittest.mock import call
from unittest.mock import MagicMock


class ApiTestCase(unittest.TestCase):

    def setUp(self):
        self.real_time = time.time
        time.time = MagicMock(return_value=1)

    def test_nonce(self):
        auth = mbm.lib.oauth.OAuth("consumer_key",
                                   "consumer_secret",
                                   "token",
                                   "token_secret")
        self.assertIsInstance(auth.nonce(), str)

    def test_authorize_request(self):
        request = MagicMock()
        request.full_url = "http://github.com?a=b&c=d"
        request.get_method = lambda: "POST"
        real_nonce = mbm.lib.oauth.OAuth.nonce
        mbm.lib.oauth.OAuth.nonce = MagicMock(return_value="1")
        auth = mbm.lib.oauth.OAuth("consumer_key",
                                   "consumer_secret",
                                   "token",
                                   "token_secret")
        auth.authorize_request(request)
        expected_calls = [
            call.add_header('oauth_consumer_key', 'consumer_key'),
            call.add_header('oauth_nonce', '1'),
            call.add_header('oauth_signature', 'gJpn5N5z9qBDiCGyxpIBsQdAgAg='),
            call.add_header('oauth_signature_method', 'HMAC-SHA1'),
            call.add_header('oauth_timestamp', '1'),
            call.add_header('oauth_token', 'token'),
            call.add_header('oauth_version', '1.0')]
        self.assertListEqual(sorted(expected_calls),
                             sorted(request.mock_calls))
        mbm.lib.oauth.OAuth.nonce = real_nonce

    def tearDown(self):
        time.time = self.real_time
