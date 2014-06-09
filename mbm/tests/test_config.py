import configparser
import os
import os.path
import unittest
import tempfile
import mbm.account


class ApiTestCase(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.conf_file = os.path.join(self.tmp_dir.name, 'test_config.ini')
        self.account = mbm.account.Account(self.conf_file)
        self.verify_cfg = configparser.ConfigParser()

    def test_new(self):
        self.assertListEqual(os.listdir(self.tmp_dir.name), [])
        self.account.new()
        self.assertIn(self.conf_file.split("/")[-1],
                      os.listdir(self.tmp_dir.name))
        self.verify_cfg.read(self.conf_file)
        self.assertDictEqual(dict(self.verify_cfg['DEFAULT']),
                             dict(self.account.config['DEFAULT']))

    def test_modify(self):
        with self.assertRaises(AttributeError):
            self.account.new_attribute
        self.account.new_attribute = "new_value"
        self.verify_cfg.read(self.conf_file)
        self.assertDictEqual(dict(self.verify_cfg['DEFAULT']),
                             dict(self.account.config['DEFAULT']))
        del self.account.new_attribute
        with self.assertRaises(AttributeError):
            self.account.new_attribute

        self.account.delete()
        self.assertEqual(dict(self.account.config['DEFAULT']), {})
        self.assertListEqual(os.listdir(self.tmp_dir.name), [])

    def tearDown(self):
        self.tmp_dir.cleanup()
