"""
Buy/Sell strategy

This whole shit is temporary, don't worry
"""

import babao.config as conf
import babao.utils.file as fu
import babao.utils.log as log
import babao.data.ledger as ledger
import babao.strategy.modelManager as modelManager

LAST_TX = None
MIN_BAL = 50  # maximum drawdown  # TODO: this should be a percent of... hmm
MIN_PROBA = 1e-2

# LABELS = {"buy": -1, "hold": 0, "sell": 1}


def initLastTransaction():
    """Initialize last transaction price"""

    global LAST_TX

    try:
        ledger_data = fu.getLastRows(conf.DB_FILE, conf.LEDGER_FRAME, 1)
        LAST_TX = {
            "time": ledger_data.index[0],
            "type": ledger_data.at[ledger_data.index[0], "type"],
            "price": ledger_data.at[ledger_data.index[0], "price"]
        }
    except (FileNotFoundError, IndexError):
        LAST_TX = {"time": None, "type": "s", "price": None}


def _tooSoon(timestamp):
    """TODO"""

    if LAST_TX["time"] \
            and timestamp - LAST_TX["time"] \
            < 3 * conf.TIME_INTERVAL * 60 * 1e9:
        log.warning("Previous transaction was too soon, waiting")
        return True
    return False


def _canBuy():
    """TODO"""

    if LAST_TX["type"] == "b":
        return False
    if ledger.BALANCE["quote"] < MIN_BAL:
        log.warning("Not enough quote to buy (aka: You're broke :/)")
        return False
    return True


def _canSell():
    """TODO"""

    if LAST_TX["type"] == "s":
        return False
    if ledger.BALANCE["crypto"] < 0.002:
        # TODO: this can be quite high actually
        # support.kraken.com/hc/en-us/articles/205893708-What-is-the-minimum-order-size-
        log.warning("Not enough crypto to sell")
        return False
    return True


def _buyOrSell(target, price, timestamp):
    """
    Decide wether to buy or sell based on the given ´target´

    It will consider the current ´ledger.BALANCE´, and evenutally update it.
    """

    global LAST_TX

    if target > MIN_PROBA:  # SELL
        if not _canSell() or _tooSoon(timestamp):
            return False
        ledger.logSell(
            ledger.BALANCE["crypto"],
            price,
            crypto_fee=ledger.BALANCE["crypto"] / 100,  # 1% fee
            timestamp=timestamp
        )
        LAST_TX["type"] = "s"

    elif target < -MIN_PROBA:  # BUY
        if not _canBuy() or _tooSoon(timestamp):  # I can english tho
            return False
        ledger.logBuy(
            ledger.BALANCE["quote"],
            price,
            quote_fee=ledger.BALANCE["quote"] / 100,  # 1% fee
            timestamp=timestamp
        )
        LAST_TX["type"] = "b"

    LAST_TX["price"] = price
    LAST_TX["time"] = timestamp

    return True


def analyse(feature_index, price, timestamp):
    """
    Apply strategy on the specified feature

    ´feature_index´ specify the row you want to use from the prepared features
    This assume you've already done ´prepareFeaturesModels()´
    """

    # TODO: ugly workaround
    # avoid problems when the features are too short (lookback)
    if (feature_index >= modelManager.FEATURES_LEN
            or modelManager.FEATURES_LEN <= 0):
        log.warning("strategy: feature_index out of range")
        return

    # TODO: use slices for training
    target_arr = modelManager.predictModels(feature_index)

    # TODO: 2d array if predict_proba
    target = target_arr[0]  # TODO: merges model (decistion tree?)

    if log.VERBOSE >= 4:
        log.debug("target:", target)

    _buyOrSell(target, price, timestamp)
