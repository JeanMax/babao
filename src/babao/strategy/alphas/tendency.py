"""
The idea of that alpha is to find local extrema,
then classify them as 0 (hold), 1 (sell), 2 (buy)
using a lstm neural network (keras)
"""

import pandas as pd
import numpy as np
import keras.models as kmod
import keras.layers as klay
import keras.utils.np_utils as kuti

import babao.utils.log as log
import babao.config as conf

MODEL = None
FEATURES = None
TARGETS = None
SCALE = 100000
FEATURES_LOOKBACK = 13  # TODO
REQUIRED_COLUMNS = [
    "vwap", "volume",
    "high", "low", "close",  # "open",
    # "SMA_vwap_3", "SMA_volume_3",
    # "SMA_vwap_2", "SMA_volume_2"
]


def _prepareFeatures(full_data, lookback):
    """
    Prepare features for training (copy)

    ´full_data´: cf. ´prepareAlphas´
    """

    def _addLookbacks(df, lookback):
        """Add lookback(s) (shifted columns) to each df columns"""

        for i in range(1, lookback + 1):
            for c in df.columns:
                if "lookback" not in c:
                    df[c + "_lookback_" + str(i)] = df[c].shift(i)
        return df.dropna()

    def _reshape(arr):
        """Reshape the features to be keras-proof"""

        return np.reshape(arr, (arr.shape[0], 1, arr.shape[1]))

    global FEATURES
    FEATURES = full_data.copy()

    # TODO: same pattern in extrema.py
    for c in FEATURES.columns:
        if c not in REQUIRED_COLUMNS:
            del FEATURES[c]

    FEATURES = _addLookbacks(scale(FEATURES), lookback)
    FEATURES = _reshape(FEATURES.values)


def _prepareTargets(full_data, lookback):
    """
    Prepare targets for training (copy)
    0 (nop), 1 (sell), 2 (buy)

    ´full_data´: cf. ´prepareAlphas´
    """

    global TARGETS

    rev = full_data["vwap"][::-1]
    TARGETS = kuti.to_categorical(
        (
            (rev.rolling(lookback).min() == rev).astype(int).replace(1, 2)
            | (rev.rolling(lookback).max() == rev).astype(int)
        ).replace(3, 0)
    )[::-1]


def prepare(full_data, targets=False):
    """
    Prepare features and targets for training (copy)

    ´full_data´: cf. ´prepareAlphas´
    """

    _prepareFeatures(full_data, FEATURES_LOOKBACK)
    if targets:
        targets_lookback = 47  # _optimizeTargets(full_data)
        _prepareTargets(full_data, targets_lookback)

        global FEATURES
        global TARGETS
        FEATURES = FEATURES[:-targets_lookback]
        TARGETS = TARGETS[FEATURES_LOOKBACK:-targets_lookback]


def train():
    """Fit the ´MODEL´"""

    log.debug("Train tendency")

    global MODEL
    if MODEL is None:
        MODEL = kmod.Sequential()
        MODEL.add(
            klay.LSTM(
                128,
                input_shape=(1, len(REQUIRED_COLUMNS) * (FEATURES_LOOKBACK + 1))
            )
        )
        MODEL.add(
            klay.Dense(
                3,
                activation='softmax'
            )
        )

        MODEL.compile(
            loss='categorical_crossentropy',
            optimizer='adam',
            metrics=['accuracy']
        )

    # this return the history... could be ploted or something
    MODEL.fit(
        FEATURES, TARGETS,
        epochs=1,  # TODO: config var?
        batch_size=1,
        shuffle=False,
        verbose=1  # TODO: check verbose level for this
    )   # TODO: make this interuptible

    # TODO: check verbose level for this
    score = MODEL.evaluate(FEATURES, TARGETS, verbose=2)
    log.debug("score:", score)


def save():
    """Save the ´MODEL´ to ´conf.ALPHA_TENDENCY_FILE´"""

    MODEL.save(conf.ALPHA_TENDENCY_FILE)


def load():
    """Load the ´MODEL´ saved in ´conf.ALPHA_TENDENCY_FILE´"""

    global MODEL
    MODEL = kmod.load_model(conf.ALPHA_TENDENCY_FILE)


def _mergeCategories(arr):
    """TODO: we could use a generic function for all alphas"""

    df = pd.DataFrame(arr, columns=["hold", "sell", "buy"])
    return (df["sell"] - df["buy"]).values


def predict(X=None):
    """
    Call predict on the current ´MODEL´

    Format the result as values between -1 (buy) and 1 (sell))
    """

    if X is None:
        X = FEATURES

    if len(X) == 1:
        X = np.array([X])

    # TODO: check verbose level for this
    return _mergeCategories(MODEL.predict_proba(X, verbose=2))


def getMergedTargets():
    """Return ´TARGETS´ in the same format than predict()"""

    if TARGETS is None or len(TARGETS) != len(FEATURES):
        return None

    return _mergeCategories(TARGETS)


# TODO: scale/unscale identicals in extrema.py
def scale(arr):
    """Scale features before train/predict"""

    return arr / SCALE


def unscale(arr):
    """Unscale features after train/predict"""

    return arr * SCALE


# def _optimizeTargets(full_data):
#     """TODO"""

#     def _buyOrSell(target, current_price, timestamp):
#         """TODO: this is very similar to strategy.strategy._buyOrSell"""

#         if ledger.BALANCE["crypto"] > 0.001 and target == 1:
#             # log.info(
#             #     "Sold for "
#             #     + str(ledger.BALANCE["crypto"])
#             #     + " crypto @ "
#             #     + str(current_price)
#             # )
#             ledger.logSell(
#                 ledger.BALANCE["crypto"],
#                 current_price,
#                 crypto_fee=ledger.BALANCE["crypto"] / 100,  # 1% fee
#                 timestamp=timestamp
#             )
#         elif ledger.BALANCE["quote"] > 0.001 and target == -1:
#             # log.info(
#             #     "Bought for "
#             #     + str(ledger.BALANCE["quote"])
#             #     + " quote @ "
#             #     + str(current_price)
#             # )
#             ledger.logBuy(
#                 ledger.BALANCE["quote"],
#                 current_price,
#                 quote_fee=ledger.BALANCE["quote"] / 100,  # 1% fee
#                 timestamp=timestamp
#             )

#     def _scoreTargets(lookback, full_data):
#         """TODO"""

#         lookback = int(lookback)  # eheh

#         _prepareTargets(full_data, lookback)
#         targets = getMergedTargets()

#         ledger.initBalance({"crypto": 0, "quote": 100})
#         for i in range(len(targets)):
#             price = unscale(FEATURES[i][0][0])  # TODO: hardcoded vwap
#             _buyOrSell(targets[i], price, full_data.index[i])

#         score = ledger.BALANCE["crypto"] * price + ledger.BALANCE["quote"]

#         log.debug(
#             "score:", int(score),
#             "lookback:", lookback
#         )

#         return -score  # TODO: compare to hold

#     # we just want the final balance
#     ledger.setLog(False)

#     res = optimize.brute(
#         _scoreTargets,
#         (slice(5, 1000, 1), ),
#         args=(full_data.reset_index(), ),
#         finish=None,
#         full_output=True
#     )

#     log.debug(repr(res))

#     return int(res[0])
