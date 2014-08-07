"""
This module contains interfaces which describe provider implementations.
"""
import abc
import urllib.parse
import uuid


class Post(abc.ABC):

    def __init__(self, account):
        self.post_data = {}
        self.http_headers = {}
        self.payload = ""
        self.account = account

    @abc.abstractmethod
    def post(self):
        raise NotImplementedError  # pragma: nocover

    def update_data(self, data):
        self.post_data.update(data)

    def update_headers(self, headers):
        self.http_headers.update(headers)

    def multipart_payload(self, b64_keys=""):
        b64_keys = b64_keys or []
        boundary = "#=#Micro-Bog-Magic#=#{}".format(uuid.uuid4())
        msg = []
        for k, v in sorted(self.post_data.items()):
            msg.append('--' + boundary)
            msg.append('Content-Disposition: form-data; name="{}"'.format(k))
            if k in b64_keys:
                msg.append('Content-Transfer-Encoding: base64')
            msg.append('')
            msg.append(v)
        msg.append('--' + boundary + '--')
        self.payload = '\r\n'.join(msg)
        self.update_headers({'Content-Type':
                             'multipart/form-data; '
                             'boundary={}'.format(boundary),
                             'Accept-Encoding': 'gzip',
                             })

    def x_www_form_payload(self):
        self.payload = "&".join(["=".join([k, urllib.parse.quote(v, safe='~')])
                                 for k, v in sorted(list(
                                     self.post_data.items()))])
        self.update_headers({'Accept-Encoding': 'gzip',
                             })


class ProviderException(Exception):
    pass
