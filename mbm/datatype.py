import abc


class Post(abc.ABC):

    @abc.abstractmethod
    def post(self):
        raise NotImplementedError  # pragma: nocover

    def update_data(self, data):
        self.post_data.update(data)


class ProviderException(Exception):
    pass
