"""
Buy/Sell strategy

This whole shit is temporary, don't worry
"""

import babao.utils.log as log
import babao.data.ledger as ledger
import babao.strategy.modelManager as modelManager

MIN_BAL = 50  # maximum drawdown
MIN_PROBA = 1e-6

# LABELS = {"buy": -1, "hold": 0, "sell": 1}


def _buyOrSell(target, current_price, timestamp):
    """
    Decide wether to buy or sell based on the given ´target´current balance

    It will consider the current ´ledger.BALANCE´, and evenutally update it.
    """

    if ledger.BALANCE["crypto"] * current_price + ledger.BALANCE["quote"] \
       < MIN_BAL:
        log.warning("You're broke :/")
        return  # TODO

    if target > MIN_PROBA and ledger.BALANCE["crypto"] > 0.001:
            ledger.logSell(
                ledger.BALANCE["crypto"],
                current_price,
                crypto_fee=ledger.BALANCE["crypto"] / 100,  # 1% fee
                timestamp=timestamp
            )
    elif target < -MIN_PROBA and ledger.BALANCE["quote"] > 0.001:
            ledger.logBuy(
                ledger.BALANCE["quote"],
                current_price,
                quote_fee=ledger.BALANCE["quote"] / 100,  # 1% fee
                timestamp=timestamp
            )


def analyse(feature_index, current_price, timestamp):
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

    _buyOrSell(target, current_price, timestamp)
