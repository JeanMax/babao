"""
Do you even lift bro?

The idea here is to give a common interface to all the alphas
so you can use these wrappers to call all of them at once.
"""

import numpy as np

import babao.utils.log as log
import babao.utils.date as du
import babao.strategy.alphas.extrema as alpha_extrema
import babao.strategy.alphas.tendency as alpha_tendency

# LABELS = {"buy": -1, "hold": 0, "sell": 1}
ALPHAS_LIST = [
    alpha_tendency,
    alpha_extrema
]  # TODO: config var eventually


def plotAlphas(full_data):
    """
    Plot all alphas

    ´full_data´ is the whole data(frame) used as feature before preparing it
    """

    def _plot(alpha):
        """TODO"""

        plot_data = full_data.copy()
        scale = plot_data["vwap"].max() * 2

        targets = alpha.getMergedTargets()
        if targets is not None:
            plot_data["y"] = targets * scale * 0.8
            plot_data["y-sell"] = plot_data["y"].where(plot_data["y"] > 0)
            plot_data["y-buy"] = plot_data["y"].where(plot_data["y"] < 0) * -1

            plot_data["y-sell"].replace(0, scale, inplace=True)
            plot_data["y-buy"].replace(0, scale, inplace=True)

        plot_data["p"] = alpha.predict() * scale
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
    for alpha in ALPHAS_LIST:
        _plot(alpha)


def prepareAlphas(full_data, targets=False):
    """
    Prepare features (and eventually targets) for all alphas

    ´full_data´ should be a dataframe of resampled values
    (conf.RESAMPLED_TRADES_COLUMNS + conf.INDICATORS_COLUMNS)
    """

    for alpha in ALPHAS_LIST:
        alpha.prepare(full_data, targets)


def trainAlphas():
    """Train all alphas and save the awesome result"""

    for alpha in ALPHAS_LIST:
        try:
            alpha.load()
        except OSError:
            log.warning("Couldn't load", alpha.__name__)
        alpha.train()
        alpha.save()


def loadAlphas():
    """Load all previous amazing alphas training"""

    for alpha in ALPHAS_LIST:
        alpha.load()


def predictAlphas(feature_index):
    """
    Predict all alphas for their given FEATURES[´feature_index´]

    Return an array of all the alphas predictions concatenated
    (which return a value between -1 (buy) and 1 (sell))

    We use that weird data structure so all features can be prepared at once,
    then the prediction can be called one after the other. This way the futures
    predictions don't influence the past ones.

    You may notice it doesn't make any sense right now! So experiment with
    neural networks and other shiny things, and if it is still useless just
    refactor it... sorry!
    """

    res = np.array([])
    for alpha in ALPHAS_LIST:
        res = np.append(
            res,
            alpha.predict(  # TODO: looping that is slow as fuck :/
                alpha.FEATURES[feature_index].reshape(1, -1)
            )
        )

    return res
