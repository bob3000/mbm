import unittest
import urllib.parse
import time
import mbm.lib.oauth

from unittest.mock import MagicMock, call, patch


class ApiTestCase(unittest.TestCase):

    def setUp(self):
        self.real_time = time.time
        time.time = MagicMock(return_value=1318622958)
        self.real_nonce = mbm.lib.oauth.nonce
        mbm.lib.oauth.nonce = MagicMock(
            return_value="kYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg")

        self.request = urllib.request
        self.http_response = MagicMock()
        self.http_response.read = lambda: urllib.parse.urlencode(
            {"oauth_token": "NPcudxy0yU5T3tBzho7iCotZ3cnetKwcTIRlX0iwRl0",
             "oauth_secret": "veNRnAWe6inFuo8o2u8SLLZLjolYDmDP7SzL0YfYI",
             "oauth_callback_confirmed": "true",
             }).encode()
        self.http_response.status = 200
        self.http_response.reason = "ERROR"

        attrs = {'urlopen.return_value': self.http_response}
        urllib.request = MagicMock()
        urllib.request.configure_mock(**attrs)

        self.request_Request = urllib.request.Request
        urllib.request.Request = MagicMock(return_value=MagicMock(
            **{'full_url': 'http://full/url',
               'get_method.return_value': 'POST',
               }))

    def test_nonce(self):
        self.assertIsInstance(mbm.lib.oauth.nonce(), str)

    def test_authorize_request(self):
        fake_request = MagicMock()
        fake_request.full_url = ("https://api.twitter.com/1/statuses/update"
                                 ".json?include_entities=true")
        fake_request.get_method = lambda: "POST"
        fake_request.data = "status=" + urllib.parse.quote(
            "Hello Ladies + Gentlemen, a signed OAuth request!")
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

    @patch("webbrowser.open_new")
    def test_authorize_user(self, webbrowser):
        args = ["cChZNFj6T5R0TigYB9yd1w",  # consumer key
                "L8qq9PZyRg6ieKGEKhZolGC0vJWLw8iEJ88DRdyOg",  # consumer secret
                "http://localhost/oauth/request_token",  # request token url
                "http://localhost/oauth/authorize",  # authorize url
                "http://localhost/oauth/callback",  # oauth callback
                "http://localhost/oauth/register_req_token"  # register token
                ]
        mbm.lib.oauth.authorize_user(*args)

        with self.assertRaises(mbm.lib.oauth.OAuthException):
            self.http_response.read = lambda: urllib.parse.urlencode(
                {"oauth_token": "NPcudxy0yU5T3tBzho7iCotZ3cnetKwcTIRlX0iwRl0",
                 "oauth_secret": "veNRnAWe6inFuo8o2u8SLLZLjolYDmDP7SzL0YfYI",
                 "oauth_callback_confirmed": "false",
                 }).encode()
            attrs = {'urlopen.return_value': self.http_response}
            urllib.request.configure_mock(**attrs)
            mbm.lib.oauth.authorize_user(*args)

        with self.assertRaises(mbm.lib.oauth.OAuthException):
            self.http_response.status = 404
            mbm.lib.oauth.authorize_user(*args)

    def tearDown(self):
        time.time = self.real_time
        mbm.lib.oauth.nonce = self.real_nonce
        urllib.request = self.request
