"""
Do you even lift bro?

The idea here is to give a common interface to all the models
so you can use these wrappers to call all of them at once.
"""

import numpy as np

import babao.utils.log as log
import babao.strategy.modelHelper as modelHelper
# import babao.strategy.models.extrema as extrema
# import babao.strategy.models.tendency as tendency
import babao.strategy.models.qlearn as qlearn


# LABELS = {"buy": -1, "hold": 0, "sell": 1}
MODELS_LIST = [
    # extrema,
    # tendency,
    qlearn,
]  # TODO: config var eventually

FEATURES_LEN = 0


def plotModels(full_data):
    """
    Plot all models

    ´full_data´ is the whole data(frame) used as feature before preparing it
    """

    for model in MODELS_LIST:
        modelHelper.plotModel(model, full_data)


def prepareModels(full_data, train_mode=False):
    """
    Prepare features (and eventually targets) for all models

    ´full_data´ should be a dataframe of resampled values
    (conf.RESAMPLED_TRADES_COLUMNS + conf.INDICATORS_COLUMNS)
    """

    len_list = []
    for model in MODELS_LIST:
        model.prepare(full_data, train_mode)
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
