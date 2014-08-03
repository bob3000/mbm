import unittest
import urllib.parse
import time
import mbm.lib.oauth

from unittest.mock import MagicMock, patch


class ApiTestCase(unittest.TestCase):

    def setUp(self):
        self.real_time = time.time
        self.real_nonce = mbm.lib.oauth.nonce
        time.time = MagicMock(return_value=1318622958)
        mbm.lib.oauth.nonce = MagicMock(
            return_value="kYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg")

        self.request = urllib.request
        self.http_response = MagicMock()
        self.http_response.read = lambda: urllib.parse.urlencode(
            {"oauth_token": "NPcudxy0yU5T3tBzho7iCotZ3cnetKwcTIRlX0iwRl0",
             "oauth_token_secret": "veNRnAWe6inFuo8o2u8SLLZLjolYDmDP7SzL0YfYI",
             "oauth_callback_confirmed": "true",
             }).encode()
        self.http_response.getcode = lambda: 200
        self.http_response.reason = lambda: "ERROR"

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
            token="370773112-GmHxMAgYyLbNEtIKZeRNFsMKPR9EyMZeS9weJAEb",
            token_secret="LswwdoUaIvS8ltyTt5jkRh4J50vUPVVHtR2YPi5kE")

        auth.authorize_request(fake_request)
        fake_request.add_header.assert_called_with(
            'Authorization',
            'OAuth oauth_consumer_key="xvz1evFS4wEEPTGEFPHBog", '
            'oauth_nonce="kYjzVBB8Y0ZFabxSWbWovY3uYSQ2pTgmZeNu2VS4cg", '
            'oauth_signature="tnnArxj06cWHq44gCs1OSKk%2FjLY%3D", '
            'oauth_signature_method="HMAC-SHA1", '
            'oauth_timestamp="1318622958", '
            'oauth_token="370773112-GmHxMAgYyLbNEtIKZeRNFsMKPR9EyMZ'
            'eS9weJAEb", '
            'oauth_version="1.0"')

    @patch("webbrowser.open_new")
    def test_authorize_user(self, webbrowser):
        args = ["http://localhost/oauth/request_token",  # request token url
                "http://localhost/oauth/authorize",  # authorize url
                "http://localhost/oauth/access",  # access url
                "http://localhost/sign-in-with-twitter/",  # oauth callback
                "http://localhost/oauth/register_req_token"  # register token
                ]
        auth = mbm.lib.oauth.OAuth(
            "cChZNFj6T5R0TigYB9yd1w",  # consumer key
            "L8qq9PZyRg6ieKGEKhZolGC0vJWLw8iEJ88DRdyOg",  # consumer secret
            "",  # token
            "")  # token secret

        time.time = MagicMock(return_value=1318467427)
        mbm.lib.oauth.nonce = MagicMock(
            return_value="ea9ec8429b68d6b77cd5600adbbb0456")

        req_mock = MagicMock()
        attrs = {'full_url': 'https://api.twitter.com/oauth/request_token',
                 'data': '',
                 'get_method.return_value': 'POST',
                 }
        req_mock.configure_mock(**attrs)
        urllib.request.Request = MagicMock(return_value=req_mock)

        auth.authorize_user(*args)
        req_mock.add_header.assert_called_with(
            'Authorization',
            'OAuth oauth_callback="http%3A%2F%2Flocalhost%2F'
            'sign-in-with-twitter%2F", '
            'oauth_consumer_key="cChZNFj6T5R0TigYB9yd1w", '
            'oauth_nonce="ea9ec8429b68d6b77cd5600adbbb0456", '
            'oauth_signature="F1Li3tvehgcraF8DMJ7OyxO4w9Y%3D", '
            'oauth_signature_method="HMAC-SHA1", '
            'oauth_timestamp="1318467427", oauth_version="1.0"')

        with self.assertRaises(mbm.lib.oauth.OAuthException):
            self.http_response.read = lambda: urllib.parse.urlencode(
                {"oauth_token": "NPcudxy0yU5T3tBzho7iCotZ3cnetKwcTIRlX0iwRl0",
                 "oauth_token_secret": "veNRnAWe6inFuo8o2u8SLLZLjolYDmDP7YfYI",
                 "oauth_callback_confirmed": "false",
                 }).encode()
            attrs = {'urlopen.return_value': self.http_response}
            urllib.request.configure_mock(**attrs)
            auth.authorize_user(*args)

        with self.assertRaises(mbm.lib.oauth.OAuthException):
            self.http_response.getcode = lambda: 404
            auth.authorize_user(*args)

    def tearDown(self):
        time.time = self.real_time
        mbm.lib.oauth.nonce = self.real_nonce
        urllib.request = self.request
