"""
Buy/Sell strategy

This whole shit is temporary, don't worry
"""

import babao.config as conf
import babao.utils.file as fu
import babao.utils.log as log
import babao.data.ledger as ledger
import babao.strategy.modelManager as modelManager

LAST_TRANSACTION_PRICE = None
LAST_TRANSACTION_TIME = None
MIN_BAL = 50  # maximum drawdown
MIN_PROBA = 1e-6

# LABELS = {"buy": -1, "hold": 0, "sell": 1}


def initLastTransactionPrice():
    """Initialize last transaction price"""

    global LAST_TRANSACTION_PRICE
    global LAST_TRANSACTION_TIME

    try:
        ledger_data = fu.getLastRows(conf.DB_FILE, conf.LEDGER_FRAME, 1)
        LAST_TRANSACTION_TIME = ledger_data.index[0]
        LAST_TRANSACTION_PRICE = ledger_data.at[ledger_data.index[0], "price"]
    except (FileNotFoundError, IndexError):
        LAST_TRANSACTION_PRICE = 0
        LAST_TRANSACTION_TIME = 0


def _buyOrSell(target, price, timestamp):
    """
    Decide wether to buy or sell based on the given ´target´current balance

    It will consider the current ´ledger.BALANCE´, and evenutally update it.
    """

    global LAST_TRANSACTION_PRICE
    global LAST_TRANSACTION_TIME

    if ledger.BALANCE["crypto"] * price + ledger.BALANCE["quote"] < MIN_BAL:
        log.warning("You're broke :/")
        return  # TODO

    if timestamp - LAST_TRANSACTION_TIME < 3 * conf.TIME_INTERVAL * 60 * 1e9:
        log.warning("Previous transaction was too soon, waiting")
        return  # TODO

    if target > MIN_PROBA:
        if ledger.BALANCE["crypto"] * price < 0.1:
            log.warning("Not enough crypto to sell")
            return
        ledger.logSell(
            ledger.BALANCE["crypto"],
            price,
            crypto_fee=ledger.BALANCE["crypto"] / 100,  # 1% fee
            timestamp=timestamp
        )

    elif target < -MIN_PROBA:
        if ledger.BALANCE["quote"] < 0.1:
            log.warning("Not enough quote to buy")
            return
        ledger.logBuy(
            ledger.BALANCE["quote"],
            price,
            quote_fee=ledger.BALANCE["quote"] / 100,  # 1% fee
            timestamp=timestamp
        )

    LAST_TRANSACTION_PRICE = price
    LAST_TRANSACTION_TIME = timestamp


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
    log.debug("target:", target) # DEBUG

    _buyOrSell(target, price, timestamp)
