"""
A class hierarchy implementing persistent configurations
"""

import abc
import configparser
import importlib
import logging
import os
import os.path

import mbm.provider


DEFAULT_GLOBAL_CONF_PATH = "~/.mbm"
DEFAULT_ACCOUNTS_PATH = "~/.mbm/accounts"


def logger(module_name):
    logger = logging.getLogger(module_name)
    logger.setLevel(logging.ERROR)
    return logger


log = logger(__name__)


def expand_dir(dir):
    return os.path.abspath(os.path.expanduser(os.path.expandvars(dir)))


def prepare_conf_dirs(global_conf_path, accounts_path):
    global_conf_path = expand_dir(global_conf_path)
    accounts_path = expand_dir(accounts_path)
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
    """
    Classes inheriting from this class gain the ability to persist
    configurations in configuration files. Generic methods like new, delete
    and write are provided.

    FOR THE INHERITING CLASS TO WORK it has to provide a class variable called
    `DEFAULT_CONFIG` which has to be a dictionary. The dictionary contents will
    be written to a file when the new method is called.

    The inheriting class has to call the parents `__init__` method with the
    `file_path` argument. Than it has access to the `self.config` object
    provided by the parent. `self.config` is a ConfigParser object.

    Below the classes `Global` and `Account` are working examples.
    """

    def __init__(self, file_path):
        self.file_path = expand_dir(file_path)
        self.config = configparser.ConfigParser()
        self.config.read(self.file_path)
        for k, v in self.DEFAULT_CONFIG.items():
            if not self.config.has_option("DEFAULT", k):
                self.config.set("DEFAULT", k, v)

    def delete(self):
        self.config['DEFAULT'] = {}
        os.remove(self.file_path)

    def new(self):
        self.write()

    def write(self):
        with open(self.file_path, 'w') as conf_file:
            self.config.write(conf_file)

    def read(self):
        self.config.read(self.file_path)


class Global(Config):
    """
    Manages global configurations and holds a dictionary of account objects.

    >>> cfg = Global("/path/to/config_file", "/path/to/account_configs")
    >>> cfg.create_account("my_account")

    >>> cfg.accounts['my_account'].config['DEFAULT']['token']
    """

    DEFAULT_CONFIG = {'default_account': '',
                      }

    def __init__(self, file_path, accounts_path):
        super().__init__(file_path)
        self.accounts_path = expand_dir(accounts_path)
        self.accounts = {}
        for i in os.listdir(self.accounts_path):
            if i.endswith(".ini"):
                try:
                    name = i.split("/")[-1][:-4]
                    self.accounts[name] = account_factory(
                        self, os.path.join(self.accounts_path, i))
                except AccountException as e:
                    log.error("Could not instantiate account "
                              "'{}': {}".format(name, e))
                    pass

    def create_account(self, name, account_type='twitter'):
        if name in self.accounts:
            raise AccountException("Account {} already "
                                   "exists".format(name))
        config_path = os.path.join(self.accounts_path, name + ".ini")
        account = account_factory(self, config_path, account_type)
        account.new()
        self.accounts[name] = account
        return account

    def delete_account(self, name):
        if name not in self.accounts:  # in case of an errornous conf file
            for i in os.listdir(self.accounts_path):
                if i.endswith(".ini"):
                    file_name = i.split("/")[-1][:-4]
                    if file_name == name:
                        config_path = os.path.join(
                            self.accounts_path, name + ".ini")
                        os.remove(config_path)
                        log.info("Deleted errornous account '{}'".format(name))
                        return
            raise AccountException("Unknown account '{}'".format(name))
        config_path = os.path.join(self.accounts_path, name + ".ini")
        account = account_factory(self, config_path)
        account.delete()
        del self.accounts[name]

    def filter_accounts(self, list_of_names):
        for name in list_of_names:
            if name not in self.accounts:
                raise AccountException("Unknown account {}".format(name))
        return list(dict(filter(lambda x: x[0] in list_of_names,
                                self.accounts.items())).values())

    def default_account(self):
        try:
            name = self.config['DEFAULT']['default_account']
            if not name:
                raise KeyError
        except KeyError:
            raise AccountException("No default account defined")
        account = self.accounts.get(name)
        if not account:
            raise AccountException("Default account does not exist")
        return account

    def has_consumer_credentials(self, account_type):
        if not self.config.has_section(account_type):
            return False
        if not self.config[account_type].get("consumer_key"):
            return False
        if not self.config[account_type].get("consumer_secret"):
            return False
        return True


def account_factory(global_conf, conf_file_path, account_type=None):
    name = conf_file_path.split("/")[-1][:-4]
    if not account_type:
        cfg_parser = configparser.ConfigParser()
        cfg_parser.read(conf_file_path)
        try:
            account_type = cfg_parser['DEFAULT']['account_type']
        except KeyError:
            raise AccountException(
                "No type specified in config file {}".format(conf_file_path))
    try:
        importlib.import_module("mbm.provider.{}".format(account_type))
    except ImportError:
        raise AccountException("Unknown account type '{}'".format(
            account_type))
    provider = getattr(mbm.provider, account_type)
    return provider.Account(global_conf, conf_file_path, name)


class Account(Config, abc.ABC):
    """
    Account credentials and configurations. Accounts are supposed to be managed
    by an instance of the Global class.
    """

    DEFAULT_CONFIG = {'username': '',
                      'account_type': '',
                      'token': '',
                      'token_secret': '',
                      }

    def __init__(self, global_conf, file_path, name, account_type):
        super().__init__(file_path)
        self.name = name
        self.global_conf = global_conf
        self.config['DEFAULT']['account_type'] = account_type
        if not global_conf.config.has_section(account_type):
            global_conf.config.add_section(
                self.config['DEFAULT']['account_type'])
            global_conf.config.set(self.config['DEFAULT']['account_type'],
                                   "consumer_key", "")
            global_conf.config.set(self.config['DEFAULT']['account_type'],
                                   "consumer_secret", "")
            self.global_conf.write()

    def reinit(self):
        self.read()
        self.global_conf.read()
        self.__init__(self.global_conf, self.file_path, self.name)

    @abc.abstractmethod
    def get_model(self, cls):
        raise NotImplementedError  # pragma: nocover

    @property
    @abc.abstractmethod
    def token_procurer_url(self):
        raise NotImplementedError  # pragma: nocover


class AccountException(Exception):
    pass
