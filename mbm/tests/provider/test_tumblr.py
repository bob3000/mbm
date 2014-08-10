import unittest
import configparser
import os.path
import uuid
import tempfile
import mbm.provider.tumblr
import mbm.lib.api
import mbm.config

from unittest.mock import MagicMock


class TumblrTestCase(unittest.TestCase):

    def setUp(self):
        self.real_uuid4 = uuid.uuid4
        uuid.uuid4 = MagicMock(return_value="1548a043-dfb0-47bc-8741"
                               "-22d3dd92e760")
        self.real_api = mbm.lib.api.Api
        mbm.lib.api.Api = MagicMock()

        self.tmp_dir = tempfile.TemporaryDirectory()
        cfg_parser = configparser.ConfigParser()
        self.conf_file = os.path.join(self.tmp_dir.name, "tumblr.ini")
        cfg_parser.read_dict({'DEFAULT': {'username': 'tmblr_user',
                                          'account_type': 'tumblr',
                                          'token': '123token456',
                                          'token_secret': '123token_secret456',
                                          },
                              })
        with open(self.conf_file, 'w') as conf:
            cfg_parser.write(conf)

        cfg_parser.read_dict({'tumblr': {'consumer_key': 'CONSUMER_KEY',
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
        self.account = mbm.provider.tumblr.Account(
            global_conf, self.conf_file, "tumblr")
        self.account.api.post = MagicMock(return_value=self.api_response)

    def test_text(self):
        text = mbm.provider.tumblr.Text(
            self.account, "title", "body text", "tag1 tag2")
        text.post()
        self.account.api.post.assert_called_with(
            post_data='body=body%20text&tags=tag1%20tag2&title=title&type='
            'text',
            headers={'Accept-Encoding': 'gzip'}
        )
        self.account.api.post = MagicMock(return_value=self.error_api_response)
        with self.assertRaises(mbm.provider.tumblr.TumblrException):
            text.post()
        self.account.api.post = MagicMock(side_effect=mbm.lib.api.ApiException)
        with self.assertRaises(mbm.provider.tumblr.TumblrException):
            text.post()
        self.account.api.post = MagicMock(return_value=self.api_response)

    def test_model_factory(self):
        with self.assertRaises(mbm.config.AccountException):
            self.account.get_model("NonExistingClass")
        self.assertIs(self.account.get_model("Text"),
                      mbm.provider.tumblr.Text)

    def test_token_procurer_url(self):
        self.assertEqual(self.account.token_procurer_url,
                         'http://bob3000.lima-city.de/oauth/token_procurer.'
                         'php?account_type=tumblr&consumer_key=CONSUMER_KEY'
                         '&consumer_secret=CONSUMER_SECRET')

    def test_photo(self):
        with self.assertRaises(mbm.provider.tumblr.TumblrException):
            mbm.provider.tumblr.Photo(self.account, "caption", "link", "tags",
                                      source="source",
                                      data="mbm/tests/fixtures/blue.png",)
        with self.assertRaises(mbm.provider.tumblr.TumblrException):
            mbm.provider.tumblr.Photo(self.account, "caption", "link", "tags")
        photo = mbm.provider.tumblr.Photo(self.account, "caption", "link",
                                          "tags", source="source")
        photo.post()
        self.account.api.post.assert_called_with(
            post_data='--#=#Micro-Bog-Magic#=#1548a043-dfb0-47bc-8741-22d3dd92'
            'e760\r\nContent-Disposition: form-data; name="caption"\r\n\r\ncap'
            'tion\r\n--#=#Micro-Bog-Magic#=#1548a043-dfb0-47bc-8741-22d3dd92e7'
            '60\r\nContent-Disposition: form-data; name="link"\r\n\r\nlink\r\n'
            '--#=#Micro-Bog-Magic#=#1548a043-dfb0-47bc-8741-22d3dd92e760\r\nCo'
            'ntent-Disposition: form-data; name="source"\r\n\r\nsource\r\n--#='
            '#Micro-Bog-Magic#=#1548a043-dfb0-47bc-8741-22d3dd92e760\r\nConten'
            't-Disposition: form-data; name="tags"\r\n\r\ntags\r\n--#=#Micro-B'
            'og-Magic#=#1548a043-dfb0-47bc-8741-22d3dd92e760\r\nContent-Dispos'
            'ition: form-data; name="type"\r\n\r\nphoto\r\n--#=#Micro-Bog-Magi'
            'c#=#1548a043-dfb0-47bc-8741-22d3dd92e760--',
            headers={'Content-Type': 'multipart/form-data; boundary=#=#Mi'
                     'cro-Bog-Magic#=#1548a043-dfb0-47bc-8741-22d3dd92e76'
                     '0', 'Accept-Encoding': 'gzip'}
        )
        photo = mbm.provider.tumblr.Photo(self.account, "caption", "link",
                                          "tags",
                                          data="mbm/tests/fixtures/blue.png")
        photo.post()
        self.account.api.post.assert_called_with(
            headers={'Content-Type': 'multipart/form-data; boundary=#=#Mi'
                     'cro-Bog-Magic#=#1548a043-dfb0-47bc-8741-22d3dd92e76'
                     '0', 'Accept-Encoding': 'gzip'},
            post_data='--#=#Micro-Bog-Magic#=#1548a043-dfb0-47bc-8741-22d3dd92'
            'e760\r\nContent-Disposition: form-data; name="caption"\r\n\r\ncap'
            'tion\r\n--#=#Micro-Bog-Magic#=#1548a043-dfb0-47bc-8741-22d3dd92e7'
            '60\r\nContent-Disposition: form-data; name="data"\r\nContent-Tran'
            'sfer-Encoding: base64\r\n\r\niVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAIA'
            'AAACDbGyAAAAFElEQVQImWN0a9rCgASYGFABqXwAdToBhhgbeJgAAAAASUVORK5CY'
            'II=\r\n--#=#Micro-Bog-Magic#=#1548a043-dfb0-47bc-8741-22d3dd92e76'
            '0\r\nContent-Disposition: form-data; name="link"\r\n\r\nlink\r\n-'
            '-#=#Micro-Bog-Magic#=#1548a043-dfb0-47bc-8741-22d3dd92e760\r\nCon'
            'tent-Disposition: form-data; name="tags"\r\n\r\ntags\r\n--#=#Micr'
            'o-Bog-Magic#=#1548a043-dfb0-47bc-8741-22d3dd92e760\r\nContent-Dis'
            'position: form-data; name="type"\r\n\r\nphoto\r\n--#=#Micro-Bog-M'
            'agic#=#1548a043-dfb0-47bc-8741-22d3dd92e760--'
        )
        self.account.api.post = MagicMock(return_value=self.error_api_response)
        with self.assertRaises(mbm.provider.tumblr.TumblrException):
            photo.post()
        self.account.api.post = MagicMock(return_value=self.api_response)

    def tearDown(self):
        uuid.uuid4 = self.real_uuid4
        mbm.lib.api.Api = self.real_api
        self.tmp_dir.cleanup()
