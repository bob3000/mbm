import unittest
import argparse
import os
import sys
import shlex
import subprocess
import mbm.config
import mbm.controller
import mbm.__main__

from unittest.mock import MagicMock, call, patch


def namespace(contents):
    n = argparse.Namespace()
    n.__dict__.update(contents)
    return n


class MainTestCase(unittest.TestCase):

    def setUp(self):
        self.real_controller = mbm.controller
        mbm.controller = MagicMock()
        mbm.__main__.controller = MagicMock()
        attrs = {'global_conf.filter_accounts.return_value': []}
        mbm.__main__.controller.configure_mock(**attrs)
        self.real_exit = sys.exit
        sys.exit = MagicMock()
        self.real_stderr = sys.stderr
        sys.stderr = MagicMock()

    def test_args_manage_account(self):
        account = shlex.split("account list myaccount")
        result = mbm.__main__.parse_args(account)
        result = filter(lambda x: x[0] != 'func', result.__dict__.items())
        self.assertDictEqual(dict(result), {'name': 'myaccount',
                                            'action': 'list'})

    def test_args_post_text(self):
        text = shlex.split("post text --accounts=acc,acc2 --tags=tag,tag2"
                           " --title='title' --body='body'")
        result = mbm.__main__.parse_args(text)
        result = filter(lambda x: x[0] != 'func', result.__dict__.items())
        self.assertDictEqual(dict(result), {'accounts': 'acc,acc2',
                                            'body': 'body', 'tags': 'tag,tag2',
                                            'extract_title': False,
                                            'title': 'title',
                                            'verbose': False})

    def test_args_post_photo(self):
        photo = shlex.split("post photo --accounts=acc,acc2 --tags=tag,tag2"
                            " --caption=caption --link=link img_source")
        result = mbm.__main__.parse_args(photo)
        result = filter(lambda x: x[0] != 'func', result.__dict__.items())
        self.assertDictEqual(dict(result), {'verbose': False, 'link': 'link',
                                            'img_source': 'img_source',
                                            'accounts': 'acc,acc2',
                                            'caption': 'caption',
                                            'tags': 'tag,tag2'})

    @patch('mbm.__main__.controller.global_conf.create_account')
    @patch('mbm.__main__.controller.global_conf.delete_account')
    @patch('mbm.__main__.controller.global_conf.filter_accounts')
    @patch('subprocess.check_call')
    @patch('sys.stdout')
    def test_manage_account(self, stdout, check_call, filter, delete, create):
        mbm.__main__.manage_account(namespace({'action': 'new',
                                               'name': None}))
        sys.exit.assert_called_with(2)
        mbm.__main__.manage_account(namespace({'action': 'new',
                                               'name': 'acc1'}))
        create.assert_called_with("acc1")

        mbm.__main__.controller.global_conf.accounts = {'acc1': 'fake'}
        mbm.__main__.manage_account(namespace({'action': 'list',
                                               'name': None}))
        stdout.assert_has_calls([call.write('acc1'), call.write('\n')])

        mbm.__main__.manage_account(namespace({'action': 'edit',
                                               'name': 'acc1'}))
        filter.assert_called_with(['acc1'])
        check_call.assert_called
        check_call.side_effect = FileNotFoundError
        mbm.__main__.manage_account(namespace({'action': 'edit',
                                               'name': 'acc1'}))
        sys.exit.assert_called_with(1)
        sys.exit.reset_mock()
        check_call.side_effect = subprocess.CalledProcessError(
            cmd='edit', returncode=1)
        mbm.__main__.manage_account(namespace({'action': 'edit',
                                               'name': 'acc1'}))
        sys.exit.assert_called_with(1)
        sys.exit.reset_mock()
        check_call.side_effect = None

        mbm.__main__.manage_account(namespace({'action': 'delete',
                                               'name': 'acc1'}))
        delete.assert_called_with('acc1')
        create.side_effect = mbm.config.AccountException
        mbm.__main__.manage_account(namespace({'action': 'new',
                                               'name': 'acc1'}))
        sys.exit.assert_called_with(2)
        sys.exit.reset_mock()

    def test_post_text(self):
        mbm.__main__.post_text(namespace({'accounts': 'acc1,acc2',
                                          'title': 'title',
                                          'body': 'mbm/tests/fixtures/a_post',
                                          'extract_title': False,
                                          'tags': 'tag1,tag2'}))
        mbm.__main__.post_text(namespace({'accounts': 'acc1,acc2',
                                          'title': None,
                                          'body': 'mbm/tests/fixtures/a_post',
                                          'extract_title': True,
                                          'tags': 'tag1,tag2'}))
        with patch('sys.stdin') as stdin:
            stdin.read = MagicMock(
                return_value="Body comming\n from\n stdin\n")
            mbm.__main__.post_text(namespace({'accounts': 'acc1,acc2',
                                              'title': 'title',
                                              'body': '',
                                              'extract_title': False,
                                              'tags': 'tag1,tag2'}))
        mbm.__main__.controller.post_text.assert_has_calls(
            [call.post_text(
                [], 'title', 'this is a title\n\nthis is\nthe text body\n',
                'tag1,tag2')])
        with patch('mbm.__main__.controller.post_text',
                   side_effect=RuntimeError):
            mbm.__main__.post_text(namespace({'accounts': 'acc1,acc2',
                                              'title': 'title', 'body': 'body',
                                              'extract_title': False,
                                              'tags': 'tag1,tag2'}))
            sys.exit.assert_called_with(1)
        mbm.__main__.controller.mock_reset()

    def test_post_photo(self):
        mbm.__main__.post_photo(
            namespace({'accounts': 'acc1,acc2',
                       'caption': 'caption',
                       'link': 'link', 'tags': 'tag1,tag2',
                       'img_source': 'mbm/tests/fixtures/blue.png'}))
        mbm.__main__.post_photo(
            namespace({'accounts': 'acc1,acc2',
                       'caption': 'caption',
                       'link': 'link', 'tags': 'tag1,tag2',
                       'img_source': 'http://data'}))
        mbm.__main__.controller.post_photo.assert_has_calls(
            [call([], caption='caption', link='link', tags='tag1,tag2',
                  data='/home/vagrant/mbm/mbm/tests/fixtures/blue.png'),
             call([], caption='caption', link='link', source='http://data',
                  tags='tag1,tag2')])
        with patch('mbm.__main__.controller.post_photo',
                   side_effect=RuntimeError):
            mbm.__main__.post_photo(
                namespace({'accounts': 'acc1,acc2',
                           'caption': 'caption',
                           'link': 'link',
                           'tags': 'tag1,tag2',
                           'img_source': 'mbm/tests/fixtures/blue.png'}))
            sys.exit.assert_called_with(1)
        mbm.__main__.controller.mock_reset()

    def test_account_list(self):
        mbm.__main__.account_list(namespace({'accounts': 'acc1,acc2'}))
        mbm.__main__.account_list(namespace({'accounts': None}))
        mbm.__main__.controller.assert_has_calls(
            [call.global_conf.filter_accounts(['acc1', 'acc2']),
             call.global_conf.default_account()])
        with patch(
            "mbm.__main__.controller.global_conf.default_account",
                side_effect=mbm.config.AccountException):
            mbm.__main__.account_list(namespace({'accounts': None}))
            sys.exit.assert_called_with(1)
        mbm.__main__.controller.mock_reset()

    @patch('mbm.__main__.parse_args')
    def test_main(self, parse_args):
        mbm.config.DEFAULT_GLOBAL_CONF_PATH = os.path.join(
            os.getcwd(), "test_config")
        mbm.config.DEFAULT_ACCOUNTS_PATH = os.path.join(
            os.getcwd(), "test_config", "accounts")
        parse_args.return_value = namespace({'func': lambda x: x})
        mbm.__main__.main()
        self.assertTrue(mbm.controller.Controller.called)
        with patch("mbm.config.prepare_conf_dirs", side_effect=RuntimeError):
            mbm.__main__.main()
            sys.exit.assert_called_with(1)
        mbm.__main__.controller.mock_reset()

    def tearDown(self):
        mbm.controller = self.real_controller
        sys.exit = self.real_exit
        sys.stderr = self.real_stderr
