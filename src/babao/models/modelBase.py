"""TODO"""

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
    """
    Base class for any model

    inputs: Input list
    """

    @property
    @abstractmethod
    def dependencies_class(
            self
    ) -> List[Union[Type["ABCModel"], Type[ib.ABCInput]]]:
        """TODO"""
        pass

    @property
    @abstractmethod
    def need_training(self) -> bool:
        """TODO"""
        pass

    @staticmethod
    def _getNodeFromList(
            node_class: Type[NODE],
            node_list: List[NODE]
    ) -> NODE:
        """TODO"""
        return node_list[
            [n.__class__ for n in node_list].index(node_class)
        ]

    @staticmethod
    def _getNodeInstance(
            node_class: Type[NODE],
            node_list: Optional[List[NODE]] = None
    ) -> NODE:
        """TODO"""
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

    def __init__(self):
        # TODO: implementation checkup: in tests?
        # that = self.__class__
        # assert type(that.inputs) == list
        # assert issubclass(that.inputs[0], Input)
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

    def _initDeps(self):
        """TODO"""
        if not MODELS:
            # TODO: should we init lm here?
            MODELS.append(self)
            ib.INPUTS.extend(lm.LEDGERS.values())
            ib.INPUTS.extend(lm.TRADES.values())
        for node_class in self.dependencies_class:
            self.dependencies.append(self._getNodeInstance(node_class))

    @abstractmethod
    def predict(self, since):
        """TODO"""
        raise NotImplementedError("TODO")

    @abstractmethod
    def train(self, since):
        """TODO"""
        raise NotImplementedError("TODO")

    @abstractmethod
    def plot(self, since):
        """TODO"""
        raise NotImplementedError("TODO")

    @abstractmethod
    def save(self):
        """TODO"""
        raise NotImplementedError("TODO")

    @abstractmethod
    def load(self):
        """TODO"""
        raise NotImplementedError("TODO")


# def plotModel(model, full_data):
#     """Plot the given model"""

#     y = unscale(model.FEATURES)  # be sure it has been scaleFit'ed
#     # ndim should be 2/3, otherwise you deserve a crash
#     if y.ndim == 3:  # keras formated
#         y = y.reshape((y.shape[0], y.shape[2]))

#     plot_data = pd.DataFrame(y).iloc[:, :len(model.REQUIRED_COLUMNS)]
#     plot_data.columns = model.REQUIRED_COLUMNS
#     plot_data.index = full_data.index[:len(y)]
#     # TODO: these are not exactly the right indexes...

#     plot_scale = plot_data["vwap"].max() * 2

#     if hasattr(model, "TARGETS"):
#         targets = model.getMergedTargets()
#         if targets is not None:
#             plot_data["y"] = targets * plot_scale * 0.8
#             plot_data["y-sell"] = plot_data["y"].where(plot_data["y"] > 0)
#             plot_data["y-buy"] = plot_data["y"].where(plot_data["y"] < 0) * -1

#             plot_data["y-sell"].replace(0, plot_scale, inplace=True)
#             plot_data["y-buy"].replace(0, plot_scale, inplace=True)

#     plot_data["p"] = model.predict() * plot_scale
#     plot_data["p-sell"] = plot_data["p"].where(plot_data["p"] > 0)
#     plot_data["p-buy"] = plot_data["p"].where(plot_data["p"] < 0) * -1

#     for col in plot_data.columns:
#         if col not in ["vwap", "p-buy", "p-sell", "y-buy", "y-sell"]:
#             del plot_data[col]
#     du.toDatetime(plot_data)
#     plot_data.fillna(0, inplace=True)
#     return plot_data
