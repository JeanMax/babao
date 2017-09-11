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

# from sklearn.externals import joblib
import joblib  # just use pickle instead?

import babao.config as conf
import babao.utils.log as log

MODEL = None
FEATURES = None
TARGETS = None
REQUIRED_COLUMNS = [
    "vwap", "volume",
    # TODO
    # "SMA_vwap_3", "SMA_volume_3",
    # "SMA_vwap_2", "SMA_volume_2"
]


def _prepareFeatures(full_data):
    """
    Prepare features for training (copy)

    ´full_data´: cf. ´prepareAlphas´
    """

    global FEATURES
    FEATURES = full_data.copy()

    for col in FEATURES.columns:
        if col not in REQUIRED_COLUMNS:
            del FEATURES[col]

    FEATURES = preprocessing.normalize(FEATURES.values)  # TODO


def _prepareTargets(full_data, lookback=1000):
    """
    Prepare targets for training (copy)

    ´full_data´: cf. ´prepareAlphas´
    """

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

    global TARGETS
    TARGETS = _findExtrema(lookback, full_data["vwap"])


def prepare(full_data, targets=False):
    """
    Prepare features and targets for training (copy)

    ´full_data´: cf. ´prepareAlphas´
    """

    _prepareFeatures(full_data)
    if targets:
        _prepareTargets(full_data)


def train(k=3):
    """Fit the ´MODEL´"""

    log.debug("Train extrema")

    global MODEL
    MODEL = neighbors.KNeighborsClassifier(k, weights="distance")  # TODO: k
    MODEL.fit(FEATURES, TARGETS)


def save():
    """Save the ´MODEL´ to ´conf.ALPHA_EXTREMA_FILE´"""

    joblib.dump(MODEL, conf.ALPHA_EXTREMA_FILE)


def load():
    """Load the ´MODEL´ saved in ´conf.ALPHA_EXTREMA_FILE´"""

    global MODEL
    MODEL = joblib.load(conf.ALPHA_EXTREMA_FILE)


def _mergeCategories(arr):
    """TODO: we could use a generic function for all alphas"""

    df = pd.DataFrame(arr, columns=["buy", "hold", "sell"])
    return (df["sell"] - df["buy"]).values


def predict(X=None):
    """
    Call predict on the current ´MODEL´

    Format the result as values between -1 (buy) and 1 (sell))
    """

    if X is None:
        X = FEATURES

    return _mergeCategories(MODEL.predict_proba(X))


def getMergedTargets():
    """Return ´TARGETS´ in the same format than predict()"""

    if TARGETS is None or len(TARGETS) != len(FEATURES):
        return None

    return TARGETS  # this is already merged
