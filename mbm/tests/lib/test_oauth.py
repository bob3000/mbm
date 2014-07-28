import unittest
import urllib.parse
import time
import mbm.lib.oauth

from unittest.mock import call
from unittest.mock import MagicMock


class ApiTestCase(unittest.TestCase):

    def setUp(self):
        self.real_time = time.time
        time.time = MagicMock(return_value=1318622958)

    def test_nonce(self):
        self.assertIsInstance(mbm.lib.oauth.nonce(), str)

    def test_authorize_request(self):
        fake_request = MagicMock()
        fake_request.full_url = ("https://api.twitter.com/1/statuses/update"
                                 ".json?include_entities=true")
        fake_request.get_method = lambda: "POST"
        fake_request.data = "status=" + urllib.parse.quote(
            "Hello Ladies + Gentlemen, a signed OAuth request!")
        real_nonce = mbm.lib.oauth.nonce
        mbm.lib.oauth.nonce = MagicMock(
            return_value="kYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg")
        auth = mbm.lib.oauth.OAuth(
            "xvz1evFS4wEEPTGEFPHBog",  # consumer key
            "kAcSOqF21Fu85e7zjz7ZN2U4ZRhfV3WpwPAoE3Z7kBw",  # consumer secret
            "370773112-GmHxMAgYyLbNEtIKZeRNFsMKPR9EyMZeS9weJAEb",  # token
            "LswwdoUaIvS8ltyTt5jkRh4J50vUPVVHtR2YPi5kE")  # token secret

        auth.authorize_request(fake_request)
        expected_calls = [
            call.add_header('oauth_consumer_key', 'xvz1evFS4wEEPTGEFPHBog'),
            call.add_header(
                'oauth_nonce', 'kYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg'),
            call.add_header('oauth_signature', 'tnnArxj06cWHq44gCs1OSKk/jLY='),
            call.add_header('oauth_signature_method', 'HMAC-SHA1'),
            call.add_header('oauth_timestamp', '1318622958'),
            call.add_header(
                'oauth_token',
                '370773112-GmHxMAgYyLbNEtIKZeRNFsMKPR9EyMZeS9weJAEb'),
            call.add_header('oauth_version', '1.0')]
        self.assertListEqual(sorted(expected_calls),
                             sorted(fake_request.mock_calls))
        mbm.lib.oauth.nonce = real_nonce

    def tearDown(self):
        time.time = self.real_time
