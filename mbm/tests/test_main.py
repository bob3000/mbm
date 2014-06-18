import unittest
import sys
import shlex
import mbm.config
import mbm.controller
import mbm.__main__

from unittest.mock import MagicMock, call, patch


class MainTestCase(unittest.TestCase):

    def setUp(self):
        self.real_controller = mbm.controller
        mbm.controller = MagicMock()
        mbm.__main__.controller = MagicMock()
        attrs = {'global_conf.accounts.filter_accounts.return_value': []}
        mbm.__main__.controller.configure_mock(**attrs)
        self.real_exit = sys.exit
        sys.exit = MagicMock()
        self.real_stderr = sys.stderr
        sys.stderr = MagicMock()

    def test_args_manage_account(self):
        account = shlex.split("account list myaccunt")
        result = mbm.__main__.parse_args(account)
        result = filter(lambda x: x[0] != 'func', result.__dict__.items())
        self.assertDictEqual(dict(result), {'name': 'myaccunt',
                                            'action': 'list'})

    def test_args_post_text(self):
        text = shlex.split("post text --accounts=acc,acc2 --tags=tag,tag2"
                           " title body")
        result = mbm.__main__.parse_args(text)
        result = filter(lambda x: x[0] != 'func', result.__dict__.items())
        self.assertDictEqual(dict(result), {'accounts': 'acc,acc2',
                                            'body': 'body', 'tags': 'tag,tag2',
                                            'title': 'title',
                                            'verbose': False})

    def test_args_post_photo(self):
        photo = shlex.split("post photo --accounts=acc,acc2 --tags=tag,tag2"
                            " --caption=caption --link=link source")
        result = mbm.__main__.parse_args(photo)
        result = filter(lambda x: x[0] != 'func', result.__dict__.items())
        self.assertDictEqual(dict(result), {'verbose': False, 'link': 'link',
                                            'source': 'source',
                                            'accounts': 'acc,acc2',
                                            'caption': 'caption',
                                            'tags': 'tag,tag2'})

    def test_post_text(self):
        mbm.__main__.post_text({'accounts': 'acc1,acc2', 'title': 'title',
                                'body': 'body', 'tags': 'tag1,tag2'})
        mbm.__main__.controller.post_text.assert_has_calls(
            [call.post_text([], 'title', 'body', tags='tag1,tag2')])
        with patch('mbm.__main__.controller.post_text',
                   side_effect=RuntimeError):
            mbm.__main__.post_text({'accounts': 'acc1,acc2', 'title': 'title',
                                    'body': 'body', 'tags': 'tag1,tag2'})
            sys.exit.assert_called_with(1)
        mbm.__main__.controller.mock_reset()

    def test_post_photo(self):
        mbm.__main__.post_photo({'accounts': 'acc1,acc2', 'caption': 'caption',
                                 'link': 'link', 'tags': 'tag1,tag2',
                                 'source': 'data'})
        mbm.__main__.post_photo({'accounts': 'acc1,acc2', 'caption': 'caption',
                                 'link': 'link', 'tags': 'tag1,tag2',
                                 'source': 'http://data'})
        mbm.__main__.controller.post_photo.assert_has_calls(
            [call.post_photo([], caption='caption', link='link',
                             tags='tag1,tag2', data='data'),
             call.post_photo([], caption='caption', link='link',
                             source='http://data', tags='tag1,tag2')])
        with patch('mbm.__main__.controller.post_photo',
                   side_effect=RuntimeError):
            mbm.__main__.post_photo({'accounts': 'acc1,acc2',
                                     'caption': 'caption', 'link': 'link',
                                     'tags': 'tag1,tag2', 'source': 'data'})
            sys.exit.assert_called_with(1)
        mbm.__main__.controller.mock_reset()

    def test_account_list(self):
        mbm.__main__.account_list({'accounts': 'acc1,acc2'})
        mbm.__main__.account_list({})
        mbm.__main__.controller.assert_has_calls(
            [call.global_conf.accounts.filter_accounts(['acc1', 'acc2']),
             call.global_conf.accounts.default_account()])
        with patch(
            "mbm.__main__.controller.global_conf.accounts.default_account",
                side_effect=mbm.config.AccountException):
            mbm.__main__.account_list({})
            sys.exit.assert_called_with(1)
        mbm.__main__.controller.mock_reset()

    @patch('mbm.__main__.parse_args')
    def test_main(self, mock_class):
        mbm.__main__.parse_args = mock_class
        mbm.__main__.main()
        mbm.controller.assert_has_calls(
            [call.Controller('~/.mbm', '~/.mbm/accounts')])
        with patch("mbm.config.prepare_conf_dirs", side_effect=RuntimeError):
            mbm.__main__.main()
            sys.exit.assert_called_with(1)
        mbm.__main__.controller.mock_reset()

    def tearDown(self):
        mbm.controller = self.real_controller
        sys.exit = self.real_exit
        sys.stderr = self.real_stderr
