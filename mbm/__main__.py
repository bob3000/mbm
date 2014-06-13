import argparse
import sys
import urllib.parse
import mbm.controller
import mbm.config


def parse_args(command_line):
    parser = argparse.ArgumentParser(
        description="Micro Bog Magic - Multi Micro Blog Client")
    subparser = parser.add_subparsers(help="Sub commands")

    # account commands
    account_parser = subparser.add_parser("account", help="Account commands")
    account_parser.add_argument("action",
                                choices=["list", "new", "edit", "delete"],
                                help="Account administration command")
    account_parser.add_argument("name", nargs="?", help="Account name")
    account_parser.set_defaults(func=manage_account)

    # post commands
    post_parser = subparser.add_parser("post", help="Post commands")
    post_type_parser = post_parser.add_subparsers(help="Types of posts")

    # # text posts
    text_parser = post_type_parser.add_parser("text")
    text_parser.add_argument("-v", "--verbose", action="store_true",
                             help="Verbosity level")
    text_parser.add_argument("-a", "--accounts",
                             help="Coma separated list of accounts to post to")
    text_parser.add_argument("-t", "--tags",
                             help="Coma separated list of tags")
    text_parser.add_argument("title", help="Title of post")
    text_parser.add_argument("body", help="Body of post")
    text_parser.set_defaults(func=post_text)

    # # photo posts
    photo_parser = post_type_parser.add_parser("photo")
    photo_parser.add_argument("-v", "--verbose", action="store_true",
                              help="Verbosity level")
    photo_parser.add_argument("-a", "--accounts",
                              help="Coma separated list of accounts")
    photo_parser.add_argument("-t", "--tags",
                              help="Coma separated list of tags")
    photo_parser.add_argument("-c", "--caption", help="Photo caption")
    photo_parser.add_argument("-l", "--link", help="Adds a link to the photo")
    photo_parser.add_argument("source",
                              help="Can either be a local path or an URL")
    photo_parser.set_defaults(func=post_photo)

    return parser.parse_args(command_line)


def account_list(args):
    try:
        if "accounts" in args:
            return controller.global_conf.accounts.filter_accounts(
                args['accounts'].split(","))
        else:
            return list(controller.global_conf.accounts.default_account())
    except mbm.config.AccountException as e:  # pragma: no cover
        print(str(e))
        sys.exit(1)


def manage_account(args):
    pass  # pragma: no cover


def post_text(args):
    accounts = account_list(args)
    controller.post_text(accounts, args['title'],
                         args['body'], tags=args['tags'])


def post_photo(args):
    accounts = account_list(args)
    if urllib.parse.urlparse(args['source'])[0] in ("http", "https"):
        controller.post_photo(accounts, caption=args['caption'],
                              link=args['link'], tags=args['tags'],
                              source=args['source'])
    else:
        controller.post_photo(accounts, caption=args['caption'],
                              link=args['link'], tags=args['tags'],
                              data=args['source'])


def main(argv=None):
    global controller
    argv = argv if argv else sys.argv[1:]
    try:
        mbm.config.prepare_conf_dirs(mbm.config.DEFAULT_GLOBAL_CONF_PATH,
                                     mbm.config.DEFAULT_ACCOUNTS_PATH)
    except RuntimeError as e:  # pragma: no cover
        print(str(e))
        sys.exit(1)
    controller = mbm.controller.Controller(
        mbm.config.DEFAULT_GLOBAL_CONF_PATH,
        mbm.config.DEFAULT_ACCOUNTS_PATH)
    parse_args(argv)


if __name__ == "__main__":  # pragma: no cover
    main()
