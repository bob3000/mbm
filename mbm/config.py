"""
Contains account configuration and OAuth credentials
"""

import abc
import configparser
import os


CONSUMER_KEY = ""
CONSUMER_SECRET = ""


class Config(abc.ABC):

    def __init__(self, file_path):
        self.file_path = file_path
        self.config = configparser.ConfigParser()
        self.config.read(file_path)

    def delete(self):
        self.config['DEFAULT'] = {}
        os.remove(self.file_path)

    def new(self):
        self.config['DEFAULT'] = self.DEFAULT_CONFIG
        self.write()

    def write(self):
        with open(self.file_path, 'w') as conf_file:
            self.config.write(conf_file)

    def __getattr__(self, name):
        if ("config" in self.__dict__ and
                name in dict(self.config['DEFAULT'])):
            return self.config['DEFAULT'][name]
        raise AttributeError

    def __setattr__(self, name, value):
        try:
            self.config['DEFAULT'][name] = value
            self.write()
        except (AttributeError, TypeError):
            super().__setattr__(name, value)

    def __delattr__(self, name):
        try:
            del self.config['DEFAULT'][name]
            self.write()
        except (AttributeError, KeyError):
            super().__delattr__(name)


class Global(Config):

    DEFAULT_CONFIG = {'accounts_path': '',
                      }

    def __init__(self, file_path, accounts_path):
        super().__init__(file_path)
        self.file_path = file_path
        self.accounts_path = accounts_path
        self.accounts = {i.split("/")[-1][:-4]:Account(i) for i in
                         os.listdir(accounts_path) if i.endswith(".ini")}

    def create_account(self, name):
        if name in self.accounts:
            raise AccountException("Account {} already exists".format(name))
        config_path = os.path.join(self.accounts_path, name + ".ini")
        account = Account(config_path, name)
        account.new()
        self.accounts[name] = account
        return account

    def delete_account(self, name):
        if name not in self.accounts:
            raise AccountException("Unknown account: {}".format(name))
        config_path = os.path.join(self.accounts_path, name + ".ini")
        account = Account(config_path, name)
        account.delete()
        del self.accounts[name]


class Account(Config):

    DEFAULT_CONFIG = {'token': '',
                      'token_secret': '',
                      }

    def __init__(self, file_path, name):
        super().__init__(file_path)
        self.name = name

    def __eq__(self, other):
        if not isinstance(other, Account):
            raise TypeError
        return self.name == other.name


class AccountException(Exception):
    pass
