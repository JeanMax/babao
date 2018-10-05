"""Base class for any model"""

import os
from abc import ABC, abstractmethod
from typing import List, Type, Optional, TypeVar, Union

import numpy as np

import babao.config as conf
import babao.utils.log as log
import babao.inputs.ledger.ledgerManager as lm
import babao.inputs.inputBase as ib

MODELS = []  # type: List[ABCModel]

NODE = TypeVar("NODE", "ABCModel", ib.ABCInput)

os.environ['KERAS_BACKEND'] = 'theano'


def getVerbose() -> int:
    """Transform our verbose level to match keras one"""
    return int(log.VERBOSE / 2) if log.VERBOSE != 1 else 1


def reshape(arr):
    """Reshape the features to be keras-proof"""
    return np.reshape(arr, (arr.shape[0], 1, arr.shape[1]))


def addLookbacks(df, look_back):
    """Add lookback(s) (shifted columns) to each df columns"""
    for i in range(1, look_back + 1):
        for col in df.columns:
            if "lookback" not in col:
                df[col + "_lookback_" + str(i)] = df[col].shift(i)
    return df.dropna()


def addLookbacks3d(arr, look_back):
    """
    Add lookback(s) (shifted columns) to each df columns
    Reshape the features to be keras-proof (3d)
    """

    res = None
    for i in range(len(arr) - look_back):
        if res is None:
            res = np.array([arr[i:i + look_back]])
        else:
            res = np.append(
                res,
                np.array([arr[i: i + look_back]]),
                axis=0
            )
    return res[look_back:]  # dropna


class ABCModel(ABC):
    """Base class for any model """

    @property
    @abstractmethod
    def dependencies_class(
            self
    ) -> List[Union[Type["ABCModel"], Type[ib.ABCInput]]]:
        """
        List of models or inputs needed by the current model

        These should be class, not instances!
        """
        pass

    @property
    @abstractmethod
    def need_training(self) -> bool:
        """Specify if the current model need to be trained"""
        pass

    @staticmethod
    def _getNodeFromList(
            node_class: Type[NODE],
            node_list: List[NODE]
    ) -> NODE:
        """Find a node instance in the MODELS list, or throw an error"""
        return node_list[
            [n.__class__ for n in node_list].index(node_class)
        ]

    @staticmethod
    def _getNodeInstance(
            node_class: Type[NODE],
            node_list: Optional[List[NODE]] = None
    ) -> NODE:
        """Find a node instance in the MODELS list, or instantiate a new one"""
        if node_list is None:
            if issubclass(node_class, ib.ABCInput):
                node_list = ib.INPUTS
                # elif issubclass(node_class, ABCModel):
            else:  # we are all grown up here
                node_list = MODELS
        try:
            return ABCModel._getNodeFromList(node_class, node_list)
        except ValueError:
            pass
        node = node_class()  # recursive horror
        # the node_class wasn't in the list so we instantiate it...
        # but its dependencies may have added and instance of node_class!
        if node_class in [n.__class__ for n in node_list]:
            return ABCModel._getNodeFromList(node_class, node_list)
        node_list.append(node)  # TODO: sort the MODELS by priority order
        return node

    def _initDeps(self):
        """Instantiate all the needed dependencies"""
        if not MODELS:
            MODELS.append(self)
            ib.INPUTS.extend(lm.LEDGERS.values())
            ib.INPUTS.extend(lm.TRADES.values())
        for node_class in self.dependencies_class:
            self.dependencies.append(self._getNodeInstance(node_class))

    def __init__(self):
        self.model = None
        self.model_file = os.path.join(
            conf.DATA_DIR, self.__class__.__name__ + ".model"
        )
        try:
            self.load()
        except OSError:
            log.warning("Couldn't load", self.__class__.__name__)
        self.dependencies = []
        self._initDeps()

    @abstractmethod
    def predict(self, since):
        """Return a dataframe of prediction starting from ´since´ timestamp"""
        raise NotImplementedError("Implement me!")

    @abstractmethod
    def train(self, since):
        """
        Train the model with data starting from ´since´ timestamp

        Return the score of model.
        """
        raise NotImplementedError("Implement me!")

    @abstractmethod
    def plot(self, since):
        """Plot the model predictions from ´since´ timestamp"""
        raise NotImplementedError("Implement me!")

    @abstractmethod
    def save(self):
        """Save the model to self.model_file"""
        raise NotImplementedError("Implement me!")

    @abstractmethod
    def load(self):
        """Load the model from self.model_file"""
        raise NotImplementedError("Implement me!")
