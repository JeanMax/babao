"""
TODO
"""

import numpy as np
import pandas as pd
import scipy.optimize as optimize

import babao.utils.log as log
import babao.config as conf
import babao.data.indicators as indic
import babao.data.ledger as ledger
import babao.strategy.modelHelper as modelHelper
from sklearn.grid_search import ParameterGrid

FEATURES = None

BUY = 0
SELL = 1
NUM_ACTIONS = 2  # [buy, sell]

MIN_BAL = 66  # maximum drawdown

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

    global FEATURES
    FEATURES = full_data.copy()

    # TODO: same pattern in extrema.py
    for c in FEATURES.columns:
        if c not in REQUIRED_COLUMNS:
            del FEATURES[c]

    FEATURES = modelHelper.scale_fit(FEATURES)
    # if not train_mode: add macd?


def _buy(price, index):
    """TODO: this is very similar to strategy.strategy._buyOrSell"""

    if ledger.BALANCE["quote"] > 0.001:
        ledger.logBuy(
            ledger.BALANCE["quote"],
            price,
            quote_fee=ledger.BALANCE["quote"] / 100,  # 1% fee
            timestamp=index
        )


def _sell(price, index):
    """TODO: this is very similar to strategy.strategy._buyOrSell"""

    if ledger.BALANCE["crypto"] > 0.001:
        ledger.logSell(
            ledger.BALANCE["crypto"],
            price,
            crypto_fee=ledger.BALANCE["crypto"] / 100,  # 1% fee
            timestamp=index
        )


def _gameOver(price):
    """Check if you're broke"""

    return bool(
        ledger.BALANCE["crypto"] * price + ledger.BALANCE["quote"]
        < MIN_BAL
    )


def _play(look_back_a_delay, look_back_b_delay, signal_delay):
    """TODO"""

    if log.VERBOSE >= 4:
        log.debug(
            "Testing params:",
            look_back_a_delay, look_back_b_delay, signal_delay
        )

    global FEATURES
    FEATURES["MACD"] = indic.MACD(
        FEATURES["vwap"],
        look_back_a_delay,
        look_back_b_delay,
        signal_delay
    )
    ledger.initBalance({"crypto": 0, "quote": 100})

    first_price = None
    price = None
    for index, feature in enumerate(FEATURES.values):
        macd = feature[1]
        if np.isnan(macd):
            continue
        price = modelHelper.unscale(feature[0])
        if first_price is None:
            first_price = price

        if macd > 0:
            _buy(price, index)
        else:
            _sell(price, index)

        if _gameOver(price):
            if log.VERBOSE >= 4:
                log.warning("game over:", index, "/", len(FEATURES))
            return -42

    score = ledger.BALANCE["crypto"] * price + ledger.BALANCE["quote"]
    hodl = price / first_price * 100

    if log.VERBOSE >= 4:
        log.debug(
            "score:", int(score - hodl),
            "(" + str(int(score)) + "-" + str(int(hodl)) + ")"
        )

    return score #- hodl


def train():
    """Fit the ´MODEL´"""

    log.debug("Train macd")

    ledger.setLog(False)
    ledger.setVerbose(log.VERBOSE >= 4)

    param_grid = list(ParameterGrid({
        "a": range(40, 100, 1),
        "b": range(70, 200, 1),
        "c": range(15, 30, 1),
        # 'a': [50], 'b': [75], 'c': [28],
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
        log.debug(param_grid[-i:])

    # res = optimize.brute(
    #     _play,
    #     (slice(5, 100, 1), ),
    #     args=(look_back_b_delay, look_back_a_delay),
    #     finish=None,
    #     full_output=True
    # )

    # log.debug("_bruteC:", repr(res))

    # return res[0]


def save():
    """Save the ´MODEL´ to ´conf.MODEL_MACD_FILE´"""

    # MODEL.save(conf.MODEL_MACD_FILE)
    pass  # TODO


def load():
    """Load the ´MODEL´ saved in ´conf.MODEL_MACD_FILE´"""

    # MODEL = load_model(conf.MODEL_MACD_FILE)
    pass  # TODO


def predict(X=None):
    """
    Call predict on the current ´MODEL´

    Format the result as values between -1 (buy) and 1 (sell))
    """

    if X is None:
        X = FEATURES

    if len(X) == 1:
        X = np.array([X])

    return 0  # TODO
