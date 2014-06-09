import json
import urllib.request


class Api():

    def __init__(self, oauth, url_prefix=""):
        self.url_prefix = url_prefix
        self.oauth = oauth

    def __getattr__(self, name):
        self.current_route = name.replace("_", "/")
        return self

    def __call__(self, *args, **kwargs):
        post_data = kwargs["post_data"] if "post_data" in kwargs else ""
        params = {k: v for k, v in kwargs.items() if k != "post_data"}
        url = self._url_from_method(params)
        if post_data:
            req = urllib.request.Request(
                url, data=post_data, method="POST")
            req = self.oauth.authorize_request(req)
            res = urllib.request.urlopen(req, data=post_data)
        else:
            req = urllib.request.Request(url)
            req = self.oauth.authorize_request(req)
            res = urllib.request.urlopen(req)
        return self._handle_request(res)

    def _url_from_method(self, params):
        url = "/".join([self.url_prefix.rstrip("/"), self.current_route])
        if params:
            params = sorted(["=".join(map(str, e)) for e in params.items()])
            params = "&".join(params)
            url = "?".join([url, params])
        return url

    def _handle_request(self, res):
        headers = {k.lower(): v.lower() for k, v in res.getheaders()}
        if ("content-type" not in headers or
                'application/json' not in headers['content-type']):
            raise ApiException(reason="content-type is not application/json")
        try:
            data = json.loads(res.read())
        except (TypeError, ValueError):
            raise ApiException(reason="payload is not valid json")
        return ApiResponse(data)


class ApiResponse():

    def __init__(self, data):
        self.__dict__.update(data)


class ApiException(Exception):

    def __init__(self, reason=""):
        self.reason = reason
