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
        self.post_data = {'type': post_type,
                          'tags': tags,
                          }

    def update_data(self, data):
        self.post_data.update(data)

    def post(self):
        self.account.api.post(post_data=self.post_data)


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


class TumblrException(Exception):
    pass
