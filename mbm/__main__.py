import argparse
import os
import subprocess
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
    text_parser.add_argument("-t", "--tags", default="",
                             help="Coma separated list of tags")
    text_parser.add_argument("-e", "--extract-title", action="store_true",
                             help="Treat first line of the post body ad the "
                             "post title")
    text_parser.add_argument("-f", "--title", default="", help="Title of post")
    text_parser.add_argument("-b", "--body", default="", help="Body of post")
    text_parser.set_defaults(func=post_text)

    # # photo posts
    photo_parser = post_type_parser.add_parser("photo")
    photo_parser.add_argument("-v", "--verbose", action="store_true",
                              help="Verbosity level")
    photo_parser.add_argument("-a", "--accounts",
                              help="Coma separated list of accounts")
    photo_parser.add_argument("-t", "--tags", default="",
                              help="Coma separated list of tags")
    photo_parser.add_argument("-c", "--caption", default="",
                              help="Photo caption")
    photo_parser.add_argument("-l", "--link", default="",
                              help="Adds a link to the photo")
    photo_parser.add_argument("img_source",
                              help="Can either be a local path or an URL")
    photo_parser.set_defaults(func=post_photo)

    return parser.parse_args(command_line)


def account_list(args):
    try:
        if args.accounts:
            return controller.global_conf.filter_accounts(
                args.accounts.split(","))
        else:
            return list(controller.global_conf.default_account())
    except mbm.config.AccountException as e:
        print("Error:", str(e), file=sys.stderr)
        sys.exit(1)


def manage_account(args):
    if args.action in ('new', 'edit', 'delete') and not args.name:
        print("{} account: error: the following arguments are required: "
              "name".format(sys.argv[0]), file=sys.stderr)
        sys.exit(2)
    try:
        if args.action == "list":
            for account_name in controller.global_conf.accounts:
                print(account_name)
        elif args.action == "new":
            controller.global_conf.create_account(args.name)
        elif args.action == "delete":
            controller.global_conf.delete_account(args.name)
        elif args.action == "edit":
            account = controller.global_conf.filter_accounts(
                [args.name])[0]
            editor = os.environ.get("EDITOR") or 'vi'
            try:
                subprocess.check_call([editor, account.file_path])
            except FileNotFoundError:
                print("Error: $EDITOR not set. Export variable and try again",
                      file=sys.stderr)
                sys.exit(1)
            except subprocess.CalledProcessError as e:
                print("Error: the editor returned {}".format(e.returncode),
                      file=sys.stderr)
                sys.exit(1)
    except mbm.config.AccountException as e:
        print("Error:", str(e), file=sys.stderr)
        sys.exit(2)


def post_text(args):
    try:
        accounts = account_list(args)
        if not args.body:
            body = sys.stdin.read()
        else:
            with open(mbm.config.expand_dir(args.body), 'r') as f:
                body = f.read()
        title = args.title
        if not title and args.extract_title:
            title = body.split("\n")[0]
            body = "\n".join(body.split("\n")[1:]).lstrip("\n")
        controller.post_text(accounts, title, body, args.tags)
    except (RuntimeError, FileNotFoundError) as e:
        print("Error:", str(e), file=sys.stderr)
        sys.exit(1)


def post_photo(args):
    accounts = account_list(args)
    if urllib.parse.urlparse(args.img_source)[0] in ("http", "https"):
        kwargs = dict(caption=args.caption, link=args.link,
                      tags=args.tags, source=args.img_source)
    else:
        img_source = []
        with open(mbm.config.expand_dir(args.img_source), 'r') as f:
            img_source.append(urllib.parse.quote(f.read()))
        kwargs = dict(caption=args.caption, link=args.link,
                      tags=args.tags, data=img_source)
    try:
        controller.post_photo(accounts, **kwargs)
    except RuntimeError as e:
        print("Error:", str(e), file=sys.stderr)
        sys.exit(1)


def main(argv=None):
    global controller
    argv = argv if argv else sys.argv[1:]
    try:
        mbm.config.prepare_conf_dirs(mbm.config.DEFAULT_GLOBAL_CONF_PATH,
                                     mbm.config.DEFAULT_ACCOUNTS_PATH)
    except RuntimeError as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)
    controller = mbm.controller.Controller(
        os.path.join(mbm.config.DEFAULT_GLOBAL_CONF_PATH, "global_config"),
        mbm.config.DEFAULT_ACCOUNTS_PATH)
    args = parse_args(argv)
    if 'func' in args:
        args.func(args)


if __name__ == "__main__":  # pragma: no cover
    main()
