import mbm.config
import mbm.lib.api
import mbm.lib.oauth


class Account(mbm.config.Account):

    def __init__(self, file_path, name):
        super().__init__(file_path, name)
        oauth = mbm.lib.oauth.OAuth(mbm.config.CONSUMER_KEY,
                                    mbm.config.CONSUMER_SECRET,
                                    self.config['DEFAULT']['token'],
                                    self.config['DEFAULT']['token_secret'])
        base_url = "https://api.tumblr.com/v2/blog/{}".format(
            self.config['DEFAULT']['username'])
        self.api = mbm.lib.api.Api(oauth, base_url)


class Post():

    def __init__(self, account, post_type, tags):
        self.account = account
        self.post_type = post_type
        self.tags = tags

    def post(self):
        raise NotImplementedError


class Text(Post):

    def __init__(self, account, title, body, tags=""):
        super().__init__(account, "text", tags)
        self.title = title
        self.body = body

    def post(self):
        post_data = {'type': self.post_type,
                     'tags': self.tags,
                     'title': self.title,
                     'body': self.body,
                     }
        self.account.api.post(post_data=post_data)
