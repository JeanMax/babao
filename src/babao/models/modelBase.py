"""TODO"""

from abc import ABC, abstractmethod

import babao.utils.log as log
import babao.inputs.ledger.ledgerManager as lm
from babao.inputs.inputBase import ABCInput

# TODO: not sure if I prefer globals over class attributes...
MODELS = None
INPUTS = None


def getVerbose():
    """Transform our verbose level to match keras one"""

    return int(log.VERBOSE / 2) if log.VERBOSE != 1 else 1


class ABCModel(ABC):
    """
    Base class for any model

    inputs: Input list
    """

    @property
    @abstractmethod
    def _dependencies(self):
        """TODO"""
        pass

    @property
    @abstractmethod
    def _needTraining(self):
        """TODO"""
        pass

    def __init__(self):
        # TODO: implementation checkup: in tests?
        # that = self.__class__
        # assert type(that.inputs) == list
        # assert issubclass(that.inputs[0], Input)
        try:
            self._load()
        except OSError:
            log.warning("Couldn't load", self.__class__.__name__)
        self._initDeps()

    def _initDeps(self):
        """TODO"""

        def getNodeFromList(cls):
            """TODO"""
            if issubclass(cls, ABCInput):
                node_list = INPUTS
            elif issubclass(cls, ABCModel):
                node_list = MODELS
            else:
                raise TypeError("Dependency class is not ABCInput/ABCModel")
            try:
                return node_list[[n.__class__ for n in node_list].index(cls)]
            except ValueError:
                node = cls()  # recursive horror
                if node.__class__ not in [n.__class__ for n in node_list]:
                    node_list.append(node)
                    # TODO: sort the MODELS by priority order
                    return node
                return getNodeFromList(cls)  # the try block will succeed

        global MODELS
        global INPUTS
        if MODELS is None:
            # TODO: should we init lm here?
            MODELS = list(self)
            INPUTS = list(lm.LEDGERS.values()) + list(lm.TRADES.values())
        for index, cls in self.dependencies:
            self.dependencies[index] = getNodeFromList(cls)

    @abstractmethod
    def predict(self, since):
        """TODO"""
        raise NotImplementedError("TODO")

    def train(self, since):
        """TODO"""
        if self.needTraining and self._train(since):
            self._save()

    @abstractmethod
    def _train(self, since):
        """TODO"""
        raise NotImplementedError("TODO")

    def plot(self, since):
        """TODO"""
        import matplotlib.pyplot as plt  # lazy load...
        # TODO: give names to figures, it's kinda annoying right now
        df = self._plot()
        df.plot()
        plt.show(block=False)

    @abstractmethod
    def _plot(self, since):
        """TODO"""
        raise NotImplementedError("TODO")

    @abstractmethod
    def _save(self):
        """TODO"""
        raise NotImplementedError("TODO")

    @abstractmethod
    def _load(self):
        """TODO"""
        raise NotImplementedError("TODO")
