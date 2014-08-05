import base64
import copy
import hashlib
import hmac
import os
import re
import time
import urllib


class OAuth():
    """
    Authenticate a HTTP request with OAuth headers
    """

    def __init__(self, consumer_key,
                 consumer_secret, token="", token_secret=""):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.token = token
        self.token_secret = token_secret

    def authorize_request(self, request):
        """
        Takes a request and returns it with the necessary OAuth headers
        """
        oauth_headers = {}
        oauth_headers['oauth_consumer_key'] = self.consumer_key
        oauth_headers['oauth_nonce'] = nonce()
        oauth_headers['oauth_signature_method'] = "HMAC-SHA1"
        oauth_headers['oauth_timestamp'] = str(int(time.time()))
        oauth_headers['oauth_token'] = self.token
        oauth_headers['oauth_version'] = "1.0"
        oauth_headers['oauth_signature'] = signature(
            oauth_headers, request, self.consumer_secret, self.token_secret)
        auth_header = ", ".join(['{}="{}"'.format(
            k, urllib.parse.quote(v, safe=""))
            for k, v in sorted(oauth_headers.items())])
        request.add_header("Authorization", "OAuth " + auth_header)
        return request


def nonce():
    return re.sub(r"\W", "", base64.b64encode(os.urandom(32)).decode())


def signature(oauth_headers, request, consumer_secret, token_secret):
    """
    TODO: Enable `strict_parsing=True` in parse_qsl and fix tests
    """
    url_params = urllib.parse.parse_qsl(
        urllib.parse.urlparse(request.full_url)[4])
    body = urllib.parse.parse_qsl(request.data)
    headers = list(copy.deepcopy(oauth_headers).items())
    params = ["=".join((urllib.parse.quote(k, safe="~"),
                        urllib.parse.quote(v, safe="~")))
              for k, v in headers + url_params + body]
    params_str = "&".join(sorted(params))
    url = request.full_url.split("?").pop(0)
    sig_base_str = "&".join([request.get_method().upper(),
                             urllib.parse.quote(url, safe="~"),
                             urllib.parse.quote(params_str, safe="~")])
    signing_key = "&".join([urllib.parse.quote(consumer_secret, safe="~"),
                            urllib.parse.quote(token_secret, safe="~")])
    return base64.b64encode(
        hmac.new(signing_key.encode(), msg=sig_base_str.encode(),
                 digestmod=hashlib.sha1).digest()).decode()


class OAuthException(Exception):
    pass
