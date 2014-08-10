import gzip
import json
import urllib.error
import urllib.request
import mbm.lib.oauth


class Api():
    """
    Translates method names into api routes and issues an request.

    In order to issue a GET request to
    'http://api.domain.com/posts/text?api_token=123'
    you would do the following:

    >>> api = Api(oauth, "http://api.domain.com")
    >>> api.posts_text(api_token="abc123")
    <ApiResponse ...>

    All given method parameters are turned to URL parameters.

    Adding a parameter named 'post_data' with a dictionary as it's value will
    result in a POST request body taken form the given dictionary. The requests
    content type will be application/x-www-form-urlencoded.

    >>> api.posts_text(post_data={'name': 'new post',
    ...                           'content': 'post content'})
    <ApiResponse ...>
    """

    def __init__(self, oauth, base_url, url_suffix=""):
        self.base_url = base_url
        self.url_suffix = url_suffix
        self.oauth = oauth
        self.current_route = ""

    def __getattr__(self, name):
        self.current_route += "/" + name
        return self

    def __call__(self, params=None, post_data=None, headers=None):
        params = params or {}
        post_data = post_data or {}
        headers = headers or {}
        url = self._url_from_method(params)
        if post_data:
            req = urllib.request.Request(
                url, headers=headers, data=post_data.encode(), method="POST")
        else:
            req = urllib.request.Request(url, headers=headers,
                                         method="GET")
        try:
            exclude_params = ('multipart/form-data' in
                              headers.get('Content-Type', ""))
            req = self.oauth.authorize_request(
                req, exclude_params=exclude_params)
            res = urllib.request.urlopen(req)
        except (urllib.error.HTTPError, mbm.lib.oauth.OAuthException) as e:
            raise ApiException(e)
        self.current_route = ""
        return self._handle_response(res)

    def _url_from_method(self, params):
        url = self.base_url.rstrip("/") + self.current_route + self.url_suffix
        if params:
            params = sorted(["=".join(map(str, e)) for e in params.items()])
            params = "&".join(params)
            url = "?".join([url, params])
        return url

    def _handle_response(self, res):
        headers = {k.lower(): v.lower() for k, v in res.getheaders()}
        if ('application/json' not in headers.get('content-type', "")):
            raise ApiException("content-type is not application/json")
        try:
            try:
                data = json.loads(gzip.decompress(res.read()).decode())
            except OSError:  # response seems not to be gzipped
                data = json.loads(res.read().decode())
        except (TypeError, ValueError):
            raise ApiException("payload is not valid json")
        return ApiResponse(data, res.getcode())


class ApiResponse():

    def __init__(self, payload, code):
        self.payload = payload
        self.code = code


class ApiException(Exception):
    pass
