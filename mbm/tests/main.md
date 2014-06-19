# main integration test

## preparation

The only thing which shall be patched in this integration is the
`urllib.request.urlopen` function in order to avoid sending real HTTP request
against some API.

    >>> import urllib.request
    >>> from unittest.mock import MagicMock
    >>> urllib.request.urlopen = MagicMock()

The mock needs to return an object which offers all the used methods from the
`http.client.HTTPResponse` class for the whole program to work.

    >>> import http.client
    >>> fake_response = MagicMock(spec_set=http.client.HTTPResponse)
    >>> fake_response_methods = {
    ...     "getheaders.return_value": [("content-type", "application/json")],
    ...     "read.return_value": '{"title": "a title", "body": "msg body"}',
    ...     "getcode.return_value": 200,
    ...     }
    >>> fake_response.configure_mock(**fake_response_methods)
    >>> urllib.request.urlopen.return_value = fake_response

Another thing we don't want is an editor to open when we call account edit
commands. Therefore we have to patch the `subprocess.check_call` method.

    >>> import subprocess
    >>> subprocess.check_call = MagicMock(return_value=0)

Next we want to make sure that all the configurations the application creates
and uses is placed inside of our project so we can inspect it manually after a
test run and clean it up properly. To get there we overwrite the defaults in
the `mbm.config` module.

    >>> import os
    >>> import shutil
    >>> import mbm.config
    >>> mbm.config.DEFAULT_GLOBAL_CONF_PATH = os.path.join(
    ...     os.getcwd(), "test_config")
    >>> mbm.config.DEFAULT_ACCOUNTS_PATH = os.path.join(
    ...     os.getcwd(), "test_config", "accounts")
    >>> shutil.rmtree(mbm.config.DEFAULT_GLOBAL_CONF_PATH, ignore_errors=True)

All the following integration test will pass the entire program logic without
involving calls to a shell for velocity reasons. Instead the input normally
is directly injected into the `main` method. The `sh` method used here
contains a little magic which can be found in the test packages `__init__.py`.
The given string corresponds exactly to the regular command line.

## account administration tests

The following tests illustrate the behavior of the `account` subcommand.

    >>> sh("mbm account list")
    >>> sh("mbm account new newaccount")

## posting tests

### text posting

### picture posting


