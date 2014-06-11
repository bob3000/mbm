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

    def test_account(self):
        mbm.provider.tumblr.Account(self.tmp_file, "tumblr")

    def tearDown(self):
        self.oauth_patcher.stop()
        self.api_patcher.stop()
        self.tmp_dir.cleanup()
