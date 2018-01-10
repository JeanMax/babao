"""
Do you even lift bro?

The idea here is to give a common interface to all the models
so you can use these wrappers to call all of them at once.
"""

import numpy as np
import pandas as pd

import babao.utils.log as log
import babao.utils.date as du
import babao.strategy.models.extrema as model_extrema
import babao.strategy.models.tendency as model_tendency

# LABELS = {"buy": -1, "hold": 0, "sell": 1}
MODELS_LIST = [
    model_extrema,
    model_tendency,
]  # TODO: config var eventually

FEATURES_LEN = 0


def plotModels(full_data):
    """
    Plot all models

    ´full_data´ is the whole data(frame) used as feature before preparing it
    """

    def _plot(model):
        """Plot the given model"""

        y = model.unscale(model.FEATURES)
        # ndim should be 2/3, otherwise you deserve a crash
        if y.ndim == 3:  # keras formated
            y = y.reshape((y.shape[0], y.shape[2]))

        plot_data = pd.DataFrame(y).iloc[:, :len(model.REQUIRED_COLUMNS)]
        plot_data.columns = model.REQUIRED_COLUMNS
        plot_data.index = full_data.index[:len(y)]
        # TODO: these are not exactly the right indexes...

        scale = plot_data["vwap"].max() * 2

        targets = model.getMergedTargets()
        if targets is not None:
            plot_data["y"] = targets * scale * 0.8
            plot_data["y-sell"] = plot_data["y"].where(plot_data["y"] > 0)
            plot_data["y-buy"] = plot_data["y"].where(plot_data["y"] < 0) * -1

            plot_data["y-sell"].replace(0, scale, inplace=True)
            plot_data["y-buy"].replace(0, scale, inplace=True)

        plot_data["p"] = model.predict() * scale
        plot_data["p-sell"] = plot_data["p"].where(plot_data["p"] > 0)
        plot_data["p-buy"] = plot_data["p"].where(plot_data["p"] < 0) * -1

        for col in plot_data.columns:
            if col not in ["vwap", "p-buy", "p-sell", "y-buy", "y-sell"]:
                del plot_data[col]
        du.to_datetime(plot_data)
        plot_data.fillna(0, inplace=True)

        plot_data.plot()
        plt.show(block=False)

    import matplotlib.pyplot as plt
    for model in MODELS_LIST:
        _plot(model)


def prepareModels(full_data, targets=False):
    """
    Prepare features (and eventually targets) for all models

    ´full_data´ should be a dataframe of resampled values
    (conf.RESAMPLED_TRADES_COLUMNS + conf.INDICATORS_COLUMNS)
    """

    len_list = []
    for model in MODELS_LIST:
        model.prepare(full_data, targets)
        len_list.append(len(model.FEATURES))

    global FEATURES_LEN
    FEATURES_LEN = min(len_list)
    # for model in MODELS_LIST:
    #     model.FEATURES = model.FEATURES[-FEATURES_LEN:]


def trainModels():
    """Train all models and save the awesome result"""

    for model in MODELS_LIST:
        try:
            model.load()
        except OSError:
            log.warning("Couldn't load", model.__name__)
        model.train()
        model.save()


def loadModels():
    """Load all previous amazing models training"""

    for model in MODELS_LIST:
        model.load()


def predictModels(feature_index):
    """
    Predict all models for their given FEATURES[´feature_index´]

    Return an array of all the models predictions concatenated
    (which return a value between -1 (buy) and 1 (sell))

    We use that weird data structure so all features can be prepared at once,
    then the prediction can be called one after the other. This way the futures
    predictions don't influence the past ones.

    You may notice it doesn't make any sense right now! So experiment with
    neural networks and other shiny things, and if it is still useless just
    refactor it... sorry!
    """

    res = np.array([])
    for model in MODELS_LIST:
        res = np.append(
            res,
            model.predict(  # TODO: looping that is slow as fuck :/
                model.FEATURES[feature_index].reshape(1, -1)
            )
        )

    return res
