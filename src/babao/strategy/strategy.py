"""
Buy/Sell strategy

This whole shit is temporary, don't worry
"""

import babao.utils.log as log
import babao.inputs.ledger.ledgerManager as lm
import babao.strategy.modelManager as modelManager
from babao.utils.enum import CryptoEnum


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

    lm.buyOrSell(target, CryptoEnum.XBT)
