"""
Do you even lift bro?

The idea here is to give a common interface to all the alphas
so you can use these wrappers to call all of them at once.
"""

import numpy as np

import babao.strategy.alphas.extrema as alpha_extrema

# LABELS = {"buy": -1, "hold": 0, "sell": 1}
ALPHAS_LIST = [alpha_extrema]  # TODO: config var eventually


def plotAlphas(full_data):
    """
    Plot all alphas

    ´full_data´ is the whole data(frame) used as feature before preparing it
    """

    for alpha in ALPHAS_LIST:
        alpha.plot(full_data)


def prepareFeaturesAlphas(full_data):
    """
    Prepare features for all alphas

    ´full_data´ should be a dataframe of resampled values
    (conf.RESAMPLED_TRADES_COLUMNS + conf.INDICATORS_COLUMNS)
    """

    for alpha in ALPHAS_LIST:
        alpha.prepareFeatures(full_data)


def prepareTargetAlphas(full_data):
    """
    Prepare targets for all supervised alphas

    ´full_data´: cf. ´prepareFeaturesAlphas´
    """

    for alpha in ALPHAS_LIST:
        alpha.prepareTarget(full_data)


def trainAlphas():
    """Train all alphas and save the awesome result"""

    for alpha in ALPHAS_LIST:
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
        # prediction_proba = alpha.prediction_proba()
        # init first for proba
        # np.append(res, alpha.FEATURES[feature_index].reshape(1, -1), axis=0)
        res = np.append(
            res,
            alpha.predict(  # TODO: looping that is slow as fuck :/
                alpha.FEATURES[feature_index].reshape(1, -1)
            )
        )

    return res
