"""
The idea of that alpha is to find local extrema,
then classify them as minimum/nop/maximum (-1/0/1)
"""

import pandas as pd
# import numpy as np
# from scipy import optimize
from sklearn import preprocessing
from sklearn import neighbors
# from sklearn import svm
# from sklearn import tree
# from sklearn import neural_network
from sklearn.externals import joblib

import babao.config as conf

MODEL = None
FEATURES = None
TARGET = None
REQUIRED_COLUMNS = [
    "vwap", "volume",
    "SMA_vwap_3", "SMA_volume_3",
    "SMA_vwap_2", "SMA_volume_2"
]


# def _scoreExtrema(lookback, df):
#     """TODO"""

#     log.debug("lookback:", round(float(lookback), 2))

#     score = scoreTarget(findExtrema(lookback, df).values, df["vwap"].values)

#     if score == 42:
#         log.debug("FAIL - lookback:", round(float(lookback), 2))
#     else:
#         log.debug(
#             "score:", int(score),
#             "lookback:", round(float(lookback), 2)
#         )

#     return score  # TODO: compare to hold


# def _findBestExtremaLookback(df):
#     """TODO"""

#     # we just want the final balance
#     ledger.setLog(False)

#     res = optimize.brute(
#         _scoreExtrema,
#         (slice(100, 300, 5), ),
#         args=(df.reset_index(), ),
#         finish=None,
#         full_output=True
#     )

#     log.debug(repr(res))

#     return int(res[0])


def _findExtrema(lookback, prices):
    """Return a serie with values -1 (minimum), 0 (nop), or 1 (maximum)"""

    lookback = int(lookback)
    rev_prices = prices[::-1]

    return (
        (  # min forward & backward
            (prices.rolling(lookback).min() == prices)
            & ((rev_prices.rolling(lookback).min() == rev_prices)[::-1])
        ).astype(int).replace(1, -1)  # minima set to -1
    ) | (  # max forward & backward
        (prices.rolling(lookback).max() == prices)
        & ((rev_prices.rolling(lookback).max() == rev_prices)[::-1])
    ).astype(int).values  # maxima set to +1


def prepareTarget(full_data, lookback=1000):
    """
    Prepare targets for training (copy)

    ´full_data´: cf. ´prepareFeaturesAlphas´
    """

    global TARGET
    TARGET = _findExtrema(lookback, full_data["vwap"])


def prepareFeatures(full_data):
    """
    Prepare features for training (copy)

    ´full_data´: cf. ´prepareFeaturesAlphas´
    """

    global FEATURES
    FEATURES = full_data.copy()

    for col in FEATURES.columns:
        if col not in REQUIRED_COLUMNS:
            del FEATURES[col]

    FEATURES = preprocessing.normalize(FEATURES.values)


def train(k=3):
    """Fit the ´MODEL´"""

    global MODEL
    MODEL = neighbors.KNeighborsClassifier(k, weights="distance")  # TODO: k
    # MODEL = svm.SVC(
    #     random_state=1,
    #     probability=True,
    #     verbose=True
    # )
    # MODEL = tree.DecisionTreeClassifier()
    # MODEL = neural_network.MLPClassifier(
    #     random_state=1,
    #     # activation="logistic",
    #     verbose=True,
    #     # hidden_layer_sizes=(10,10,10),
    #     # shuffle=False,
    #     # tol=1e-9,
    #     # alpha=1e-6,
    #     # early_stopping=True
    # )

    MODEL.fit(FEATURES, TARGET)

    # print(repr(test_proba.where(test_proba["buy"] > 0.1).dropna()))
    # print(repr(test_proba.where(test_proba["sell"] > 0.1).dropna()))
    # print(
    #     "total:",
    #     len(test_proba.where(test_proba["buy"] > 0.1).dropna())
    #     + len(test_proba.where(test_proba["sell"] > 0.1).dropna())
    # )

    # from sklearn import metrics
    # # print(metrics.classification_report(y.values, test_target))
    # # print(metrics.confusion_matrix(y.values, test_target))
    # import matplotlib.pyplot as plt; plt.show(block=False)

    # return MODEL.score(prepared_data, prediction)


def save():
    """Save the ´MODEL´ to ´conf.ALPHA_EXTREMA_FILE´"""

    joblib.dump(MODEL, conf.ALPHA_EXTREMA_FILE)


def load():
    """Load the ´MODEL´ saved in ´conf.ALPHA_EXTREMA_FILE´"""

    global MODEL
    MODEL = joblib.load(conf.ALPHA_EXTREMA_FILE)


def predict(X=None):
    """Call predict on the current ´MODEL´"""

    if X is None:
        return MODEL.predict(FEATURES)
    return MODEL.predict(X)


def predict_proba(X=None):
    """Call predict_proba on the current ´MODEL´"""

    if X is None:
        return MODEL.predict_proba(FEATURES)
    return MODEL.predict_proba(X)


def plot(full_data):
    """
    Plot the result of predict

    ´full_data´: cf. ´prepareFeaturesAlphas´
    """

    full_data = full_data.copy()
    prediction = pd.Series(predict())
    prediction.index = full_data.index
    scale = full_data["vwap"].max()
    full_data["sell"] = prediction.where(prediction == 1) * scale
    full_data["buy"] = prediction.where(prediction == -1) * -scale
    for col in full_data.columns:
        if col not in ["vwap", "sell", "buy"]:
            del full_data[col]
    full_data = full_data.fillna(0)
    full_data.index = pd.to_datetime(full_data.index, unit="us")
    full_data.plot()
    import matplotlib.pyplot as plt
    plt.show(block=False)


def plot_proba(full_data):
    """
    Plot the result of predict_proba

    ´full_data´: cf. ´prepareFeaturesAlphas´
    """

    full_data = full_data.copy()
    prediction = pd.DataFrame(predict_proba(), columns=["sell", "hold", "buy"])
    prediction.index = full_data.index
    scale = full_data["vwap"].max() * 3
    full_data["sell"] = prediction["sell"] * scale
    full_data["buy"] = prediction["buy"] * scale
    for col in full_data.columns:
        if col not in ["vwap", "sell", "buy"]:
            del full_data[col]
    full_data = full_data.fillna(0)
    full_data.index = pd.to_datetime(full_data.index, unit="us")
    full_data.plot()
    import matplotlib.pyplot as plt
    plt.show(block=False)
