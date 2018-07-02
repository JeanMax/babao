"""TODO"""

from abc import ABC, abstractmethod


class ABCModel(ABC):
    """
    Base class for any model

    inputs: Input list
    """

    @property
    @abstractmethod
    def dependencies(self):
        """TODO"""
        pass

    def __init__(self):
        # implementation checkup:
        # that = self.__class__
        # assert type(that.inputs) == list
        # assert issubclass(that.inputs[0], Input)

    @abstractmethod
    def train(self, since):
        raise NotImplementedError("TODO")

    @abstractmethod
    def predict(self, since):
        raise NotImplementedError("TODO")

    @abstractmethod
    def save(self):
        raise NotImplementedError("TODO")

    @abstractmethod
    def load(self):
        raise NotImplementedError("TODO")
