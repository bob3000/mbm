import abc


class Text(abc.ABC):

    @abc.abstractmethod
    def post(self):
        raise NotImplementedError
