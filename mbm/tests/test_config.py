import configparser
import os
import os.path
import unittest
import tempfile
import mbm.config
import mbm.provider.tumblr


class GlobalConfigTestCase(unittest.TestCase):

    def setUp(self):
        self.real_tumblr_account = mbm.provider.tumblr.Account
        mbm.provider.tumblr.Account = type("Account", (mbm.config.Account,),
                                           {'get_model': lambda: "model"})
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.conf_file = os.path.join(self.tmp_dir.name, 'test_config.ini')
        self.accounts_dir = os.path.join(self.tmp_dir.name, "accounts")
        os.mkdir(self.accounts_dir)
        self.verify_cfg = configparser.ConfigParser()
        self.config = mbm.config.Global(self.conf_file,
                                        self.accounts_dir)

    def test_accounts(self):
        self.config.new()
        self.assertIn(self.conf_file.split("/")[-1],
                      os.listdir(self.tmp_dir.name))
        self.assertDictEqual(mbm.config.Global.DEFAULT_CONFIG,
                             dict(self.config.config['DEFAULT']))

        self.assertListEqual(os.listdir(self.accounts_dir), [])
        self.assertDictEqual(self.config.accounts, {})
        self.config.create_account("account1", account_type="tumblr")
        self.assertIn("account1", self.config.accounts)
        self.assertListEqual(os.listdir(self.accounts_dir), ["account1.ini"])
        with self.assertRaises(mbm.config.AccountException):
            self.config.create_account("account1")
        self.config.delete_account("account1")
        self.assertListEqual(os.listdir(self.accounts_dir), [])
        self.assertDictEqual(self.config.accounts, {})
        with self.assertRaises(mbm.config.AccountException):
            self.config.delete_account("account1")

    def test_modify(self):
        with self.assertRaises(AttributeError):
            self.config.new_attribute
        self.config.new_attribute = "new_value"
        self.verify_cfg.read(self.conf_file)
        self.assertDictEqual(dict(self.verify_cfg['DEFAULT']),
                             dict(self.config.config['DEFAULT']))
        with self.assertRaises(AttributeError):
            del self.config.non_existing_attribute
        del self.config.new_attribute
        with self.assertRaises(AttributeError):
            self.config.new_attribute

    def test_delete(self):
        self.config.new()
        self.config.delete()
        self.assertEqual(dict(self.config.config['DEFAULT']), {})
        self.assertListEqual(os.listdir(self.tmp_dir.name), ["accounts"])

    def test_not_type_given(self):
        with open(os.path.join(self.accounts_dir, "empty_conf.ini"), 'w') as f:
            f.write("[DEFAULT]")
        with self.assertRaises(mbm.config.AccountException):
            self.config.create_account("empty_conf")

    def tearDown(self):
        self.tmp_dir.cleanup()
        mbm.provider.tumblr.Account = self.real_tumblr_account
