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
        plot_data = self._getPlotData()
        plot_data.plot()
        plt.show(block=False)

    @abstractmethod
    def _getPlotData(self, since):
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


# def plotModel(model, full_data):
#     """Plot the given model"""

#     y = unscale(model.FEATURES)  # be sure it has been scale_fit'ed
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
#     du.to_datetime(plot_data)
#     plot_data.fillna(0, inplace=True)
#     return plot_data
