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
        mbm.provider.tumblr.Account = type(
            "Account", (mbm.config.Account,),
            {'get_model': lambda: "model",
             'procure_oauth_credentials': lambda: "credentials",
             })
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.conf_file = os.path.join(self.tmp_dir.name, 'test_config.ini')
        self.accounts_dir = os.path.join(self.tmp_dir.name, "accounts")
        os.mkdir(self.accounts_dir)
        self.verify_cfg = configparser.ConfigParser()
        self.config = mbm.config.Global(self.conf_file, self.accounts_dir)

    def test_prepare_conf_dirs(self):
        global_conf_path = os.path.join(self.tmp_dir.name, "c", "my_conf")
        accounts_path = os.path.join(
            self.tmp_dir.name, "c", "my_conf", "accounts")
        mbm.config.prepare_conf_dirs(global_conf_path, accounts_path)
        mbm.config.prepare_conf_dirs(global_conf_path, accounts_path)
        self.assertTrue(os.path.exists(global_conf_path))
        self.assertTrue(os.path.exists(accounts_path))
        os.rmdir(accounts_path)
        os.chmod(global_conf_path, 0o444)
        with self.assertRaises(RuntimeError):
            mbm.config.prepare_conf_dirs(global_conf_path, accounts_path)
        os.rmdir(global_conf_path)
        os.chmod(global_conf_path.rsplit("/", maxsplit=1)[0], 0o444)
        with self.assertRaises(RuntimeError):
            mbm.config.prepare_conf_dirs(global_conf_path, accounts_path)

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

    def test_delete(self):
        self.config.new()
        self.config.delete()
        self.assertEqual(dict(self.config.config['DEFAULT']), {})
        self.assertListEqual(os.listdir(self.tmp_dir.name), ["accounts"])

    def test_not_type_given(self):
        with open(os.path.join(self.accounts_dir, "empty_conf.ini"), 'w') as f:
            f.write("[DEFAULT]")
        with self.assertRaises(mbm.config.AccountException):
            self.config.create_account("empty_conf", account_type=None)

    def test_filter_accounts(self):
        self.config.accounts = {'accX': 'X', 'accY': 'Y', 'accZ': 'Z'}
        self.assertListEqual(self.config.filter_accounts(['accX']), ['X'])
        with self.assertRaises(mbm.config.AccountException):
            self.config.filter_accounts(['non_existing_account'])
        self.config.accounts = {}

    def test_default_account(self):
        self.config.accounts = {'accX': 'X', 'accY': 'Y', 'accZ': 'Z'}
        self.config.config['DEFAULT']['default_account'] = "accX"
        self.assertEqual(self.config.default_account(), "X")
        self.config.accounts = {}
        with self.assertRaises(mbm.config.AccountException):
            self.config.default_account()
        del self.config.config['DEFAULT']['default_account']
        with self.assertRaises(mbm.config.AccountException):
            self.config.default_account()

    def test_has_consumer_credentials(self):
        self.assertFalse(self.config.has_consumer_credentials("account_type"))
        self.config.config.add_section("account_type")
        self.assertFalse(self.config.has_consumer_credentials('account_type'))
        self.config.config.set("account_type", "consumer_key", "12345")
        self.assertFalse(self.config.has_consumer_credentials('account_type'))
        self.config.config.set("account_type", "consumer_secret", "12345")
        self.assertTrue(self.config.has_consumer_credentials('account_type'))

    def tearDown(self):
        self.tmp_dir.cleanup()
        mbm.provider.tumblr.Account = self.real_tumblr_account
