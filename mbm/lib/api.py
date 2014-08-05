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

    def __init__(self, oauth, base_url):
        self.base_url = base_url
        self.oauth = oauth

    def __getattr__(self, name):
        self.current_route = name.replace("_", "/")
        return self

    def __call__(self, *args, **kwargs):
        post_data = kwargs["post_data"] if "post_data" in kwargs else ""
        params = {k: v for k, v in kwargs.items() if k != "post_data"}
        url = self._url_from_method(params)
        if post_data:
            data = urllib.parse.urlencode(sorted(list(post_data.items())))
            req = urllib.request.Request(
                url, data=data.encode(), method="POST")
        else:
            req = urllib.request.Request(url, method="GET")
        try:
            req = self.oauth.authorize_request(req)
            res = urllib.request.urlopen(req)
        except (urllib.error.HTTPError, mbm.lib.oauth.OAuthException) as e:
            raise ApiException(e)
        return self._handle_response(res)

    def _url_from_method(self, params):
        url = "/".join([self.base_url.rstrip("/"), self.current_route])
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
