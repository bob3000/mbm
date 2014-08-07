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
        super().__init__(global_conf, file_path, name)
        self.oauth = mbm.lib.oauth.OAuth(
            self.global_conf.config['twitter']['consumer_key'],
            self.global_conf.config['twitter']['consumer_secret'],
            token=self.config['DEFAULT']['token'],
            token_secret=self.config['DEFAULT']['token_secret'])
        base_url = "https://api.twitter.com/1.1/"
        url_suffix = ".json"
        self.api = mbm.lib.api.Api(self.oauth, base_url, url_suffix=url_suffix)

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
            self.global_conf.config['twitter']['consumer_key'],
            self.global_conf.config['twitter']['consumer_secret']]]
        params = ["=".join([k, v]) for k, v in zip(param_keys, params_vals)]
        return TOKEN_PROCURER_BASE_URL+"?"+"&".join(params)


class Post(mbm.datatype.Post):

    def __init__(self, account, post_type, tags):
        self.account = account
        self.post_data = {'type': post_type,
                          'tags': tags,
                          }

    def post(self):
        try:
            res = self.account.api.post(post_data=self.post_data)
        except mbm.lib.api.ApiException as e:
            raise TwitterException(e)
        if res.code != 200:
            raise TwitterException(
                "Twitter API responded with code {}: {}".format(
                    res.code, res.payload))


class Text(Post):

    def __init__(self, account, title, body, tags):
        super().__init__(account, "text", tags)
        self.update_data({'title': title,
                          'body': body,
                          })


class Photo(Post):

    def __init__(self, account, caption, link, tags, data="", source=""):
        if all((source, data)) or not any((source, data)):
            raise TwitterException("Either 'source' or 'data' must be present")
        super().__init__(account, "photo", tags)
        self.update_data({'caption': caption,
                          'link': link,
                          })
        if source:
            self.update_data({'source': source})
        else:
            with open(data, 'rb') as f:
                photo = base64.b64encode(f.read())
            self.update_data({'data': photo.decode()})


class TwitterException(mbm.datatype.ProviderException):
    pass
