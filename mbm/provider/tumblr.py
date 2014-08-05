import mbm.config
import mbm.lib.api
import mbm.lib.oauth
import mbm.datatype
import urllib


REQUEST_TOKEN_URL = "http://www.tumblr.com/oauth/request_token"
AUTHORIZE_URL = "http://www.tumblr.com/oauth/authorize"
ACCESS_URL = "http://www.tumblr.com/oauth/access_token"
TOKEN_PROCURER_BASE_URL = ("http://bob3000.lima-city.de"
                           "/oauth/token_procurer.php")


class Account(mbm.config.Account):

    def __init__(self, global_conf, file_path, name):
        super().__init__(global_conf, file_path, name)
        self.oauth = mbm.lib.oauth.OAuth(
            self.global_conf.config['tumblr']['consumer_key'],
            self.global_conf.config['tumblr']['consumer_secret'],
            token=self.config['DEFAULT']['token'],
            token_secret=self.config['DEFAULT']['token_secret'])
        base_url = "https://api.tumblr.com/v2/blog/{}".format(
            self.config['DEFAULT']['username'])
        self.api = mbm.lib.api.Api(self.oauth, base_url)
        param_keys = ['request_url', 'authorize_url', 'access_url',
                      'consumer_key', 'consumer_secret']
        params_vals = [urllib.parse.quote(i, safe="~") for i in [
            REQUEST_TOKEN_URL, AUTHORIZE_URL, ACCESS_URL,
            self.global_conf.config['tumblr']['consumer_key'],
            self.global_conf.config['tumblr']['consumer_secret']]]
        params = ["=".join([k, v]) for k, v in zip(param_keys, params_vals)]
        self.token_procurer_url = TOKEN_PROCURER_BASE_URL+"?"+"&".join(params)

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

    def reinit(self):
        self.read()
        self.global_conf.read()
        self.__init__(self.global_conf, self.file_path, self.name)


class Post(mbm.datatype.Post):

    def __init__(self, account, post_type, tags):
        self.account = account
        self.post_data = {'type': post_type,
                          'tags': tags,
                          }

    def post(self):
        res = self.account.api.post(post_data=self.post_data)
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
            self.update_data({'data': data})


class TumblrException(mbm.datatype.ProviderException):
    pass
