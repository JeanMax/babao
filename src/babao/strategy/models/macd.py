"""
Simple MACD based model,
with a very elegant algorithm (aka: brute-force)
"""

import pickle
import numpy as np
from sklearn.grid_search import ParameterGrid

import babao.utils.log as log
import babao.config as conf
import babao.data.indicators as indic
import babao.data.ledger as ledger
import babao.strategy.transaction as tx
# import babao.strategy.modelHelper as modelHelper

MODEL = {"a": 46, "b": 75, "c": 22}
FEATURES = None
FEATURES_DF = None

REQUIRED_COLUMNS = [
    "vwap",  # "volume",
    # "high", "low",
    # "close", "open",
]


def prepare(full_data, train_mode=False):
    """
    Prepare features and targets for training (copy)

    ´full_data´: cf. ´prepareModels´
    """

    def _reshape(arr):
        """Reshape the features to be keras-proof"""

        return np.reshape(arr, (arr.shape[0], 1, arr.shape[1]))

    global FEATURES_DF
    FEATURES_DF = full_data.copy()

    # TODO: same pattern in extrema.py
    for c in FEATURES_DF.columns:
        if c not in REQUIRED_COLUMNS:
            del FEATURES_DF[c]

    # TODO: I'm not so sure about scaling
    # FEATURES_DF = modelHelper.scale_fit(FEATURES_DF)
    if not train_mode:
        FEATURES_DF["MACD"] = indic.MACD(
            FEATURES_DF["vwap"], MODEL["a"], MODEL["b"], MODEL["c"]
        )
        FEATURES_DF.dropna(inplace=True)

    global FEATURES
    FEATURES = _reshape(FEATURES_DF.values)


def _play(look_back_a_delay, look_back_b_delay, signal_delay):
    """Play an epoch with the given MACD parameters"""

    if log.VERBOSE >= 4:
        log.debug(
            "Testing params:",
            look_back_a_delay, look_back_b_delay, signal_delay
        )

    global FEATURES_DF
    FEATURES_DF["MACD"] = indic.MACD(
        FEATURES_DF["vwap"],
        look_back_a_delay,
        look_back_b_delay,
        signal_delay
    )
    ledger.initBalance({"crypto": 0, "quote": 100})
    tx.initLastTransaction(readFile=False)

    first_price = None
    price = None
    for index, feature in enumerate(FEATURES_DF.values):
        macd = feature[1]
        if np.isnan(macd):
            continue
        # price = modelHelper.unscale(feature[0])
        price = feature[0]
        if first_price is None:
            first_price = price

        tx.buyOrSell(
            macd * -1,
            price,
            index * conf.TIME_INTERVAL * 60 * 10**9
        )

        if tx.gameOver(price):
            if log.VERBOSE >= 4:
                log.warning("game over:", index, "/", len(FEATURES_DF))
            return -42

    score = ledger.BALANCE["crypto"] * price + ledger.BALANCE["quote"]
    hodl = price / first_price * 100

    if log.VERBOSE >= 4:
        log.debug(
            "score:", int(score - hodl),
            "(" + str(int(score)) + "-" + str(int(hodl)) + ")"
        )

    return score  # - hodl


def train():
    """Fit the ´MODEL´"""

    log.debug("Train macd")

    ledger.setLog(False)
    ledger.setVerbose(log.VERBOSE >= 4)

    global MODEL
    param_grid = list(ParameterGrid({
        "a": range(9, 100, 1),
        "b": range(25, 200, 1),
        "c": range(10, 30, 1),
        # 'a': [MODEL['a']], 'b': [MODEL['b']], 'c': [MODEL['c']],
        "score": [-42]
    }))

    grid_len = len(param_grid)
    for i, param in enumerate(param_grid):
        if param["a"] >= param["b"]:
            continue

        param["score"] = _play(param["a"], param["b"], param["c"])

        percent = i / grid_len * 100
        if i and not bool(percent % 1):
            log.debug(
                str(int(percent)) + "% done",
                "- best yet:", sorted(param_grid, key=lambda k: k['score'])[-1]
            )

    param_grid = sorted(param_grid, key=lambda k: k['score'])
    log.debug("Top Ten:")
    for i in range(len(param_grid[-10:]), 0, -1):
        log.debug(param_grid[-i])

    MODEL = param_grid[-1]
    del MODEL["score"]


def save():
    """Save the ´MODEL´ to ´conf.MODEL_MACD_FILE´"""

    with open(conf.MODEL_MACD_FILE, "wb") as f:
        pickle.dump(MODEL, f)


def load():
    """Load the ´MODEL´ saved in ´conf.MODEL_MACD_FILE´"""

    global MODEL
    if MODEL is None:
        with open(conf.MODEL_MACD_FILE, "rb") as f:
            MODEL = pickle.load(f)


def predict(X=None):
    """
    Call predict on the current ´MODEL´

    Format the result as values between -1 (buy) and 1 (sell))
    """

    if X is None:
        X = FEATURES

    if len(X) == 1:
        return X[0][1] * -1  # TODO

    return np.delete(X, 0, 2).reshape(X.shape[0], ) * -1  # TODO
