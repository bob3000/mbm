"""
Contains account configuration and OAuth credentials
"""

import abc
import configparser
import importlib
import os
import os.path

import mbm.provider


CONSUMER_KEY = ""
CONSUMER_SECRET = ""

DEFAULT_GLOBAL_CONF_PATH = "~/.mbm"
DEFAULT_ACCOUNTS_PATH = "~/.mbm/accounts"


def prepare_conf_dirs(global_conf_path, accounts_path):
    global_conf_path = os.path.abspath(os.path.expanduser(
        os.path.expandvars(global_conf_path)))
    accounts_path = os.path.abspath(os.path.expanduser(
        os.path.expandvars(accounts_path)))
    if not os.path.exists(global_conf_path):
        try:
            os.makedirs(global_conf_path)
        except OSError:
            raise RuntimeError(
                "Could not create directory {}".format(global_conf_path))
    if not os.path.exists(accounts_path):
        try:
            os.makedirs(accounts_path)
        except OSError:
            raise RuntimeError(
                "Could not create directory {}".format(accounts_path))


class Config():

    def __init__(self, file_path):
        self.file_path = file_path
        self.config = configparser.ConfigParser()
        self.config.read(file_path)

    def delete(self):
        self.config['DEFAULT'] = {}
        os.remove(self.file_path)

    def new(self, updates=None):
        updates = updates if updates else {}
        self.config['DEFAULT'] = self.DEFAULT_CONFIG
        self.config['DEFAULT'].update(updates)
        self.write()

    def write(self):
        with open(self.file_path, 'w') as conf_file:
            self.config.write(conf_file)


class Global(Config):
    """
    Manages global configurations and holds a dictionary of account objects.

    >>> cfg = Global("/path/to/config_file", "/path/to/account_configs")
    >>> cfg.create_account("my_account")

    >>> cfg.accounts['my_account'].token
    """

    DEFAULT_CONFIG = {}

    def __init__(self, file_path, accounts_path):
        super().__init__(file_path)
        self.file_path = file_path
        self.accounts_path = accounts_path
        self.accounts = {i.split("/")[-1][:-4]: account_factory(i) for i in
                         os.listdir(accounts_path) if i.endswith(".ini")}

    def create_account(self, name, account_type=None):
        if name in self.accounts:
            raise AccountException("Account {} already exists".format(name))
        config_path = os.path.join(self.accounts_path, name + ".ini")
        account = account_factory(config_path, account_type)
        account.new()
        self.accounts[name] = account
        return account

    def delete_account(self, name):
        if name not in self.accounts:
            raise AccountException("Unknown account: {}".format(name))
        config_path = os.path.join(self.accounts_path, name + ".ini")
        account = account_factory(config_path)
        account.delete()
        del self.accounts[name]

    def filter_accounts(self, list_of_names):
        for name in list_of_names:
            if name not in self.accounts:
                raise AccountException("Unknown account: {}".format(name))
        return list(dict(filter(lambda x: x[0] in list_of_names,
                                self.accounts.items())).values())

    def default_account(self):
        try:
            name = self.config['DEFAULT']['default_account']
        except KeyError:
            raise AccountException("No default account defined.")
        account = self.accounts.get(name)
        if not account:
            raise AccountException("Default account does not exist")
        return account


def account_factory(conf_file_path, account_type=None):
    name = conf_file_path.split("/")[-1][:-4]
    if not account_type:
        cfg_parser = configparser.ConfigParser()
        cfg_parser.read(conf_file_path)
        try:
            account_type = cfg_parser['DEFAULT']['account_type']
        except KeyError:
            raise AccountException(
                "No type specified in config file {}".format(conf_file_path))
    importlib.import_module("mbm.provider.{}".format(account_type))
    provider = getattr(mbm.provider, account_type)
    return provider.Account(conf_file_path, name)


class Account(Config, abc.ABC):
    """
    Account credentials and configurations. Accounts are supposed to be managed
    by an instance of the Global class.
    """

    DEFAULT_CONFIG = {'username': '',
                      'account_type': 'tumblr',
                      'token': '',
                      'token_secret': '',
                      }

    def __init__(self, file_path, name):
        super().__init__(file_path)
        self.name = name

    @abc.abstractmethod
    def get_model(self, cls):
        raise NotImplementedError  # pragma: nocover


class AccountException(Exception):
    pass
