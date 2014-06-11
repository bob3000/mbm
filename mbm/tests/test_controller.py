import unittest
import tempfile
import mbm.config
import mbm.controller

from unittest.mock import MagicMock


class ControllerTestCase(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.real_config = mbm.config
        mbm.config = MagicMock()
        self.controller = mbm.controller.Controller(
            global_conf_path=self.tmp_dir.name,
            accounts_path=self.tmp_dir.name + "/accounts")
        self.accounts = [MagicMock(), MagicMock()]

    def test_text(self):
        self.controller.post_text(self.accounts, "title", "body", "tag,tag2")
        for account in self.accounts:
            account.get_model.assert_called_with("Text")
            account.mock_reset()

    def test_photo(self):
        self.controller.post_photo(self.accounts, caption="caption",
                                   link="link", tags="tag,tag2", data="data")
        for account in self.accounts:
            account.get_model.assert_called_with("Photo")
            account.mock_reset()

    def tearDown(self):
        mbm.config = self.real_config
        self.tmp_dir.cleanup()
