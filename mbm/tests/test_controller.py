import unittest
import tempfile
import mbm.config
import mbm.controller
import mbm.datatype

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

        attrs = {'get_model.side_effect': mbm.datatype.ProviderException}
        account_provider_exception = MagicMock()
        account_provider_exception.configure_mock(**attrs)
        self.accounts_provider_exception = [account_provider_exception,
                                            account_provider_exception]

    def test_text(self):
        self.controller.post_text(self.accounts, "title", "body", "tag,tag2")
        for account in self.accounts:
            account.get_model.assert_called_with("Text")
            account.mock_reset()
        with self.assertRaises(RuntimeError):
            self.controller.post_text(self.accounts_provider_exception,
                                      "title", "body", "tag,tag2")

    def test_photo(self):
        self.controller.post_photo(self.accounts, caption="caption",
                                   link="link", tags="tag,tag2", data="data")
        for account in self.accounts:
            account.get_model.assert_called_with("Photo")
            account.mock_reset()
        with self.assertRaises(RuntimeError):
            self.controller.post_photo(self.accounts_provider_exception,
                                       "title", "body", "tag,tag2")

    def tearDown(self):
        mbm.config = self.real_config
        self.tmp_dir.cleanup()
