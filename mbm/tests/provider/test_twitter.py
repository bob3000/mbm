import unittest
import configparser
import os.path
import tempfile
import mbm.provider.twitter
import mbm.lib.api
import mbm.config

from unittest.mock import MagicMock


class twitterTestCase(unittest.TestCase):

    def setUp(self):
        self.real_api = mbm.lib.api.Api
        mbm.lib.api.Api = MagicMock()

        self.tmp_dir = tempfile.TemporaryDirectory()
        cfg_parser = configparser.ConfigParser()
        self.conf_file = os.path.join(self.tmp_dir.name, "twitter.ini")
        cfg_parser.read_dict({'DEFAULT': {'username': 'tmblr_user',
                                          'account_type': 'twitter',
                                          'token': '123token456',
                                          'token_secret': '123token_secret456',
                                          },
                              })
        with open(self.conf_file, 'w') as conf:
            cfg_parser.write(conf)

        cfg_parser.read_dict({'twitter': {'consumer_key': 'CONSUMER_KEY',
                                          'consumer_secret': 'CONSUMER_SECRET',
                                          },
                              })
        global_conf = MagicMock(**{'config': cfg_parser})

        attrs_success = {'code': 200,
                         'payload.return_value': '\{"body": "todo bien"\}'}
        attrs_error = {'code': 404,
                       'payload.return_value': '\{"error": "todo mal"\}'}
        self.api_response = MagicMock()
        self.api_response.configure_mock(**attrs_success)
        self.error_api_response = MagicMock()
        self.error_api_response.configure_mock(**attrs_error)
        self.account = mbm.provider.twitter.Account(
            global_conf, self.conf_file, "twitter")
        self.account.api.post = MagicMock(return_value=self.api_response)

    def test_text(self):
        text = mbm.provider.twitter.Text(
            self.account, "title", "body text", "tag1 tag2")
        text.post()
        self.account.api.post.assert_called_with(
            post_data={'title': 'title', 'body': 'body text',
                       'type': 'text', 'tags': 'tag1 tag2'})
        self.account.api.post = MagicMock(return_value=self.error_api_response)
        with self.assertRaises(mbm.provider.twitter.TwitterException):
            text.post()
        self.account.api.post = MagicMock(side_effect=mbm.lib.api.ApiException)
        with self.assertRaises(mbm.provider.twitter.TwitterException):
            text.post()
        self.account.api.post = MagicMock(return_value=self.api_response)

    def test_model_factory(self):
        with self.assertRaises(mbm.config.AccountException):
            self.account.get_model("NonExistingClass")
        self.assertIs(self.account.get_model("Text"),
                      mbm.provider.twitter.Text)

    def test_token_procurer_url(self):
        self.assertEqual(self.account.token_procurer_url,
                         'http://bob3000.lima-city.de/oauth/token_procurer.'
                         'php?account_type=twitter&consumer_key=CONSUMER_KEY'
                         '&consumer_secret=CONSUMER_SECRET')

    def test_photo(self):
        with self.assertRaises(mbm.provider.twitter.TwitterException):
            mbm.provider.twitter.Photo(self.account, "caption", "link", "tags",
                                       source="source",
                                       data="mbm/tests/fixtures/blue.png",)
        with self.assertRaises(mbm.provider.twitter.TwitterException):
            mbm.provider.twitter.Photo(self.account, "caption", "link", "tags")
        photo = mbm.provider.twitter.Photo(self.account, "caption", "link",
                                           "tags", source="source")
        photo.post()
        self.account.api.post.assert_called_with(
            post_data={'type': 'photo', 'tags': 'tags',
                       'source': 'source', 'caption': 'caption',
                       'link': 'link'})
        photo = mbm.provider.twitter.Photo(self.account, "caption", "link",
                                           "tags",
                                           data="mbm/tests/fixtures/blue.png")
        photo.post()
        self.account.api.post.assert_called_with(
            post_data={
                'type': 'photo', 'tags': 'tags',
                'data': 'iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAIAAAACDbGyAAAAFElE'
                        'QVQImWN0a9rCgASYGFABqXwAdToBhhgbeJgAAAAASUVORK5CYII=',
                'caption': 'caption', 'link': 'link'})
        self.account.api.post = MagicMock(return_value=self.error_api_response)
        with self.assertRaises(mbm.provider.twitter.TwitterException):
            photo.post()
        self.account.api.post = MagicMock(return_value=self.api_response)

    def tearDown(self):
        mbm.lib.api.Api = self.real_api
        self.tmp_dir.cleanup()
