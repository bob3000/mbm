import base64
import copy
import hashlib
import hmac
import os
import re
import time
import urllib.parse
import urllib.request


class OAuth():
    """
    Authenticate a HTTP request with OAuth headers
    """

    def __init__(self, consumer_key, consumer_secret, token, token_secret):
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
        oauth_headers['oauth_nonce'] = self.nonce()
        oauth_headers['oauth_signature_method'] = "HMAC-SHA1"
        oauth_headers['oauth_timestamp'] = str(int(time.time()))
        oauth_headers['oauth_token'] = self.token
        oauth_headers['oauth_version'] = "1.0"
        oauth_headers['oauth_signature'] = _signature(
            oauth_headers, request, self.consumer_secret, self.token_secret)
        for k, v in oauth_headers.items():
            request.add_header(k, v)
        return request

    def nonce(self):
        return re.sub(r"\W", "", base64.b64encode(os.urandom(32)).decode())


def _signature(oauth_headers, request, consumer_secret, token_secret):
    url_params = urllib.parse.parse_qsl(
        urllib.parse.urlparse(request.full_url)[4])
    body = urllib.parse.parse_qsl(request.data)
    headers = list(copy.deepcopy(oauth_headers).items())
    headers_params_body = headers + url_params + body
    params = ["=".join((urllib.parse.quote(k), urllib.parse.quote(v)))
              for k, v in headers_params_body]
    params_str = "&".join(sorted(params))
    url = request.full_url.split("?").pop(0)
    sig_base_str = "&".join([request.get_method().upper(),
                             urllib.parse.quote(url, safe=""),
                             urllib.parse.quote(params_str, safe="")])
    signing_key = "&".join([urllib.parse.quote(consumer_secret),
                            urllib.parse.quote(token_secret)])
    return base64.b64encode(
        hmac.new(signing_key.encode(), msg=sig_base_str.encode(),
                 digestmod=hashlib.sha1).digest()).decode()
