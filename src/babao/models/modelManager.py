"""
Do you even lift bro?

The idea here is to give a common interface to all the models
so you can use these wrappers to call all of them at once.
TODO
"""

import babao.models.modelBase as mb


def plotModels(since):
    """
    Plot all models

    ´full_data´ is the whole data(frame) used as feature before preparing it
    TODO
    """

    for model in mb.MODELS:
        model.plot(since)


def trainModels(since):
    """Train all models and save the awesome result"""

    for model in mb.MODELS:
        model.train()


def predictModels(since):
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

    TODO
    """

    # res = np.array([])
    # for model in mb.MODELS:
    #     res = np.append(
    #         res,
    #         model.predict(  # TODO: looping that is slow as fuck :/
    #             model.FEATURES[feature_index].reshape(1, -1)
    #         )
    #     )

    # return res

    return mb.MODELS[0].predict(since)


# def prepareModels(full_data, train_mode=False):
#     """
#     Prepare features (and eventually targets) for all models

#     ´full_data´ should be a dataframe of resampled values
#     (conf.RESAMPLED_TRADES_COLUMNS + conf.INDICATORS_COLUMNS)
#     TODO
#     """

#     len_list = []
#     for model in mb.MODELS:
#         model.prepare(full_data, train_mode)
#         len_list.append(len(model.FEATURES))

#     global FEATURES_LEN
#     FEATURES_LEN = min(len_list)
#     # for model in mb.MODELS:
#     #     model.FEATURES = model.FEATURES[-FEATURES_LEN:]
