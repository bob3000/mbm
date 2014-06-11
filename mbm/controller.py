import mbm.config


class Controller():

    def __init__(self, global_conf_path="~/.mbm",
                 accounts_path="~/.mbm/accounts"):
        mbm.config.prepare_conf_dirs(global_conf_path, accounts_path)
        self.global_conf = mbm.config.Global(global_conf_path, accounts_path)

    def post_text(self, accounts, title, body, tags=""):
        for account in accounts:
            text = account.get_model("Text")(title, body, tags)
            text.post()

    def post_photo(self, accounts, caption="",
                   link="", tags="", data="", source=""):
        for account in accounts:
            photo = account.get_model("Photo")(
                caption, link, tags, data, source)
            photo.post()
