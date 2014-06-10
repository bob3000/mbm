import configparser
import os
import os.path
import unittest
import tempfile
import mbm.config


class GlobalConfigTestCase(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.conf_file = os.path.join(self.tmp_dir.name, 'test_config.ini')
        self.accounts_dir = os.path.join(self.tmp_dir.name, "accounts")
        os.mkdir(self.accounts_dir)
        self.verify_cfg = configparser.ConfigParser()
        self.config = mbm.config.Global(self.conf_file,
                                        self.accounts_dir)

    def test_accounts(self):
        self.assertListEqual(os.listdir(self.accounts_dir), [])
        self.assertDictEqual(self.config.accounts, {})
        self.config.create_account("account1")
        self.assertIn("account1", self.config.accounts)
        self.assertListEqual(os.listdir(self.accounts_dir), ["account1.ini"])
        with self.assertRaises(mbm.config.AccountException):
            self.config.create_account("account1")
        self.config.delete_account("account1")
        self.assertListEqual(os.listdir(self.accounts_dir), [])
        self.assertDictEqual(self.config.accounts, {})
        with self.assertRaises(mbm.config.AccountException):
            self.config.delete_account("account1")

    def test_new(self):
        self.config.new()
        self.assertIn(self.conf_file.split("/")[-1],
                      os.listdir(self.tmp_dir.name))
        self.assertDictEqual(mbm.config.Global.DEFAULT_CONFIG,
                             dict(self.config.config['DEFAULT']))

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
        self.config.delete()
        self.assertEqual(dict(self.config.config['DEFAULT']), {})
        self.assertListEqual(os.listdir(self.tmp_dir.name), ["accounts"])

    def test_account_equality(self):
        self.assertEqual(mbm.config.Account("path", "name"),
                         mbm.config.Account("path123", "name"))
        self.assertNotEqual(mbm.config.Account("path", "other_name"),
                            mbm.config.Account("path123", "name"))
        with self.assertRaises(TypeError):
            mbm.config.Account("path", "name") == "string"

    def tearDown(self):
        self.tmp_dir.cleanup()
