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
    >>> fake_response_methods = {
    ...     "getheaders.return_value": [("content-type", "application/json")],
    ...     "read.return_value": b'{"title": "a title", "body": "msg body"}',
    ...     "getcode.return_value": 200,
    ...     }

An alternate return value for oauth logic used for obtaining access tokens.

    >>> fake_oauth_response_methods = {
    ...     "getheaders.return_value": [("content-type",
    ...                                  "application/x-www-form-urlencoded")],
    ...     "read.return_value": b'oauth_token=NPcudxy0yU5T3tBzho7iCotZ3cnetKw'
    ...                          b'cTIRlX0iwRl0&oauth_token_secret=veNRnAWe6i'
    ...                          b'nFuo8o2u8SLLZLjolYDmDP7SzL0YfYI'
    ...                          b'&oauth_callback_confirmed=true',
    ...     "getcode.return_value": 200,
    ...     }

    >>> fake_response = MagicMock(spec_set=http.client.HTTPResponse)
    >>> urllib.request.urlopen.return_value = fake_response
    >>> fake_response.configure_mock(**fake_oauth_response_methods)

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
    >>> sh("mbm account list")
    newaccount
    >>> sh("mbm account new newaccount")
    Error: Account newaccount already exists
    >>> sh("mbm account edit non_existing_account")
    Error: Unknown account non_existing_account

The `account edit` command would normally open an editor

    >>> sh("mbm account edit newaccount")
    >>> sh("mbm account delete newaccount")
    >>> sh("mbm account delete newaccount")
    Error: Unknown account 'newaccount'
    >>> sh("mbm account list")

## posting tests

The `post` subcommand allows to post different types of data. In the following
we are going to show the behavior of every single post type.
The return value of the mocked urlopen method has to be changed to fit the
program logic.

    >>> fake_response.configure_mock(**fake_response_methods)

### text posting

    >>> sh("mbm post text --title 'a title' "
    ...    "--body 'mbm/tests/fixtures/a_post'")
    Error: No default account defined

Need to change the urlopen mock payload again.

    >>> fake_response.configure_mock(**fake_oauth_response_methods)
    >>> sh("mbm account new myaccount")
    >>> fake_response.configure_mock(**fake_response_methods)

Text posting either works by giving an explicit title and a path to a file
which contains the post body or by piping text to stdin.

    >>> sh("mbm post text --account=myaccount --tags=tag1,tag2 "
    ...    "--title='a title' --body='mbm/tests/fixtures/a_post'")

If the `--extract-title` option is given the first line of the body will be
treated as the post title and will be removed from the body. An explicit given
title will overwrite the `--extract-title` option.

    >>> sh("mbm post text --account=myaccount --tags=tag1,tag2 "
    ...    "--extract-title --body='mbm/tests/fixtures/a_post'")

Next we will reconficure the mocked response so it will bring up an error.

    >>> fake_response_methods.update({"getcode.return_value": 404})
    >>> fake_response.configure_mock(**fake_response_methods)

    >>> sh("mbm post text --account=myaccount --title='a title' "
    ...    "--body='mbm/tests/fixtures/a_post'")
    Error: Tumblr API responded with code 404: ...

### picture posting

The last argument of the command line is the source which can either be an url
or a filename.

    >>> sh("mbm post photo --account=myaccount mbm/tests/fixtures/a_post")
    Error: Tumblr API responded with code 404: ...

Make the fake response return something positive again.

    >>> fake_response_methods.update({"getcode.return_value": 200})
    >>> fake_response.configure_mock(**fake_response_methods)

    >>> sh("mbm post photo --account=myaccount mbm/tests/fixtures/a_post")
    >>> sh("mbm post photo --account=myaccount --caption=caption --link=link "
    ...    "--tags=tag1,tag2 http://www.some.url.net")

