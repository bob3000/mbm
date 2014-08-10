import base64
import urllib
import mbm.config
import mbm.lib.api
import mbm.lib.oauth
import mbm.datatype


TOKEN_PROCURER_BASE_URL = ("http://bob3000.lima-city.de"
                           "/oauth/token_procurer.php")


class Account(mbm.config.Account):

    def __init__(self, global_conf, file_path, name):
        super().__init__(global_conf, file_path, name, 'tumblr')
        self.oauth = mbm.lib.oauth.OAuth(
            self.global_conf.config['tumblr']['consumer_key'],
            self.global_conf.config['tumblr']['consumer_secret'],
            token=self.config['DEFAULT']['token'],
            token_secret=self.config['DEFAULT']['token_secret'])
        base_url = "http://api.tumblr.com/v2/blog/{}.tumblr.com".format(
            self.config['DEFAULT']['username'])
        self.api = mbm.lib.api.Api(self.oauth, base_url)

    def get_model(self, cls):
        """
        Returns one of the data model classes in this module which fits to this
        account type.
        """
        try:
            return globals()[cls]
        except KeyError:
            raise mbm.config.AccountException(
                "Data model {} does not exist".format(cls))

    @property
    def token_procurer_url(self):
        param_keys = ['account_type', 'consumer_key', 'consumer_secret']
        params_vals = [urllib.parse.quote(i, safe="~") for i in [
            self.config['DEFAULT']['account_type'],
            self.global_conf.config['tumblr']['consumer_key'],
            self.global_conf.config['tumblr']['consumer_secret']]]
        params = ["=".join([k, v]) for k, v in zip(param_keys, params_vals)]
        return TOKEN_PROCURER_BASE_URL+"?"+"&".join(params)


class Post(mbm.datatype.Post):

    def __init__(self, account, post_type, tags):
        super().__init__(account)
        self.account = account
        self.post_data = {'type': post_type,
                          'tags': tags,
                          }

    def post(self):
        try:
            if 'data' in self.post_data:
                res = self.account.api.post(
                    post_data=self.payload, headers=self.headers)
            else:
                res = self.account.api.post(
                    post_data=self.payload, headers=self.headers)
        except mbm.lib.api.ApiException as e:
            raise TumblrException(e)
        if res.code != 200:
            raise TumblrException(
                "Tumblr API responded with code {}: {}".format(
                    res.code, res.payload))


class Text(Post):

    def __init__(self, account, title, body, tags):
        super().__init__(account, "text", tags)
        self.update_data({'title': title,
                          'body': body,
                          })
        self.x_www_form_payload()


class Photo(Post):

    def __init__(self, account, caption, link, tags, data="", source=""):
        if all((source, data)) or not any((source, data)):
            raise TumblrException("Either 'source' or 'data' must be present")
        super().__init__(account, "photo", tags)
        self.update_data({'caption': caption,
                          'link': link,
                          })
        if source:
            self.update_data({'source': source})
        else:
            with open(data, 'rb') as f:
                photo = base64.b64encode(f.read()).decode()
            self.update_data({'data': photo})
        self.multipart_payload(b64_keys=['data'])


class TumblrException(mbm.datatype.ProviderException):
    pass
