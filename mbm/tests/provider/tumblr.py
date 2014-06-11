import unittest
import configparser
import os.path
import tempfile
import mbm.provider.tumblr
import mbm.lib.oauth
import mbm.lib.api
import mbm.config

from unittest.mock import patch


class TumblrTestCase(unittest.TestCase):

    def setUp(self):
        self.oauth_patcher = patch('mbm.lib.oauth.OAuth')
        self.api_patcher = patch('mbm.lib.api.Api')
        self.oauth_patcher.start()
        self.api_patcher.start()
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.tmp_file = os.path.join(self.tmp_dir.name, "tumblr.ini")
        cfg_parser = configparser.ConfigParser()
        cfg_parser.read_dict({'DEFAULT': {'username': 'tmblr_user',
                                          'account_type': 'tumblr',
                                          'token': '123token456',
                                          'token_secret': '123token_secret456',
                                          },
                              })
        with open(self.tmp_file, 'w') as conf:
            cfg_parser.write(conf)
        self.account = mbm.provider.tumblr.Account(self.tmp_file, "tumblr")

    def test_model_factory(self):
        with self.assertRaises(mbm.config.AccountException):
            self.account.get_model("NonExistingClass")
        self.assertIs(self.account.get_model("Text"),
                      mbm.provider.tumblr.Text)

    def test_text(self):
        text = mbm.provider.tumblr.Text(
            self.account, "title", "body text", "tag1 tag2")
        text.post()
        self.account.api.post.assert_called_with(
            post_data={'title': 'title', 'body': 'body text',
                       'type': 'text', 'tags': 'tag1 tag2'})

    def test_photo(self):
        with self.assertRaises(mbm.provider.tumblr.TumblrException):
            mbm.provider.tumblr.Photo(self.account, "caption", "link", "tags",
                                      source="source", data="data",)
        with self.assertRaises(mbm.provider.tumblr.TumblrException):
            mbm.provider.tumblr.Photo(self.account, "caption", "link", "tags")
        photo = mbm.provider.tumblr.Photo(self.account, "caption", "link",
                                          "tags", source="source")
        photo.post()
        self.account.api.post.assert_called_with(
            post_data={'type': 'photo', 'tags': 'tags',
                       'source': 'source', 'caption': 'caption',
                       'link': 'link'})
        photo = mbm.provider.tumblr.Photo(self.account, "caption", "link",
                                          "tags", data="data")
        photo.post()
        self.account.api.post.assert_called_with(
            post_data={'type': 'photo', 'tags': 'tags',
                       'data': 'data', 'caption': 'caption',
                       'link': 'link'})

    def tearDown(self):
        self.oauth_patcher.stop()
        self.api_patcher.stop()
        self.tmp_dir.cleanup()
