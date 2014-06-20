import mbm.config
import mbm.datatype


class Controller():

    def __init__(self, global_conf_path, accounts_path):
        self.global_conf = mbm.config.Global(global_conf_path, accounts_path)

    def post_text(self, accounts, title, body, tags):
        for account in accounts:
            try:
                text = account.get_model("Text")(account, title, body, tags)
                text.post()
            except mbm.datatype.ProviderException as e:
                raise RuntimeError(e)

    def post_photo(self, accounts, caption="",
                   link="", tags="", data="", source=""):
        for account in accounts:
            try:
                photo = account.get_model("Photo")(
                    account, caption, link, tags, data, source)
                photo.post()
            except mbm.datatype.ProviderException as e:
                raise RuntimeError(e)
