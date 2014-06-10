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
        oauth_headers['oauth_signature'] = self._signature(
            oauth_headers, request)
        for k, v in oauth_headers.items():
            request.add_header(k, v)
        return request

    def nonce(self):
        return re.sub(r"\W", "", base64.b64encode(os.urandom(32)).decode())

    def _signature(self, oauth_headers, request):
        url_params = ([] if "?" not in request.full_url else
                      [tuple(i.split("=")) for i in
                       request.full_url.split("?").pop().split("&")])
        headers_n_params = sorted(
            list(copy.deepcopy(oauth_headers).items()) + url_params)
        headers_n_params_str = "&".join(["=".join(
            (urllib.parse.quote(k.encode()), urllib.parse.quote(v.encode())))
            for k, v in headers_n_params])
        sig_base_str = "&".join([request.get_method(),
                                 urllib.parse.quote(request.full_url),
                                 urllib.parse.quote(headers_n_params_str)])
        signing_key = "&".join([urllib.parse.quote(self.consumer_secret),
                                urllib.parse.quote(self.token_secret)])
        return base64.b64encode(
            hmac.new(signing_key.encode(), msg=sig_base_str.encode(),
                     digestmod=hashlib.sha1).digest()).decode()
