"""
Contains account configuration and OAuth credentials
"""

import configparser
import os


CONSUMER_KEY = ""
CONSUMER_SECRET = ""
DEFAULT_CONFIG = {'token': '',
                  'token_secret': '',
                  }


class Account():

    def __init__(self, file_path):
        self.file_path = file_path
        self.config = configparser.ConfigParser()
        self.config.read(file_path)

    def new(self):
        self.config['DEFAULT'] = DEFAULT_CONFIG
        self.write()

    def delete(self):
        self.config['DEFAULT'] = {}
        os.remove(self.file_path)

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
        except AttributeError:
            super().__setattr__(name, value)

    def __delattr__(self, name):
        try:
            del self.config['DEFAULT'][name]
            self.write()
        except AttributeError:
            super().__delattr__(name)
