import urllib.request


class Api():

    def __init__(self, url_prefix=""):
        self.url_prefix = url_prefix

    def __getattr__(self, name):
        self.current_route = name.replace("_", "/")
        return self

    def __call__(self, *args, **kwargs):
        post_data = kwargs["post_data"] if "post_data" in kwargs else ""
        params = {k: v for k, v in kwargs.items() if k != "post_data"}
        url = self.url_from_method(params)
        if post_data:
            urllib.request.urlopen(url, data=post_data)
        else:
            urllib.request.urlopen(url)

    def url_from_method(self, params):
        url = "/".join([self.url_prefix.rstrip("/"), self.current_route])
        if params:
            params = ["=".join(map(str, e)) for e in params.items()]
            params.sort()
            params = "&".join(params)
            url = "?".join([url, params])

        return url
