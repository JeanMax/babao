"""
The idea of that model is to find local extrema,
then classify them as 0 (hold), 1 (sell), 2 (buy)
using a lstm neural network (keras)
"""

import pandas as pd
import numpy as np

import babao.utils.log as log
import babao.config as conf
import babao.data.indicators as indic
import babao.strategy.modelHelper as modelHelper

MODEL = None
FEATURES = None
TARGETS = None

FEATURES_LOOKBACK = 0  # TODO

REQUIRED_COLUMNS = [
    "vwap",  # "volume",
    # "high", "low",
    # "close", "open",
]
INDICATORS_COLUMNS = [
    "SMA_vwap_9", "SMA_vwap_26", "SMA_vwap_77", "SMA_vwap_167",
    # "SMA_volume_9", "SMA_volume_26", "SMA_volume_77",
    "MACD_vwap_9_26_10", "MACD_vwap_26_77_10"
]

BATCH_SIZE = 1
HIDDEN_SIZE = 32
EPOCHS = 5


def _prepareFeatures(full_data, lookback):
    """
    Prepare features for training (copy)

    ´full_data´: cf. ´prepareModels´
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

    FEATURES = indic.get(FEATURES, INDICATORS_COLUMNS).dropna()
    FEATURES = modelHelper.scale_fit(FEATURES)
    FEATURES = _addLookbacks(FEATURES, lookback)
    FEATURES = _reshape(FEATURES.values)


def _prepareTargets(full_data, lookback):
    """
    Prepare targets for training (copy)
    0 (nop), 1 (sell), 2 (buy)

    ´full_data´: cf. ´prepareModels´
    """

    global TARGETS
    from keras.utils.np_utils import to_categorical  # lazy load...

    rev = full_data["vwap"][::-1]
    TARGETS = to_categorical(
        (
            (rev.rolling(lookback).min() == rev).astype(int).replace(1, 2)
            | (rev.rolling(lookback).max() == rev).astype(int)
        ).replace(3, 0)
    )[::-1]


def prepare(full_data, train_mode=False):
    """
    Prepare features and targets for training (copy)

    ´full_data´: cf. ´prepareModels´
    """

    _prepareFeatures(full_data, FEATURES_LOOKBACK)
    if train_mode:
        targets_lookback = 47  # _optimizeTargets(full_data)
        _prepareTargets(full_data, targets_lookback)

        global FEATURES
        global TARGETS
        FEATURES = FEATURES[:-targets_lookback]
        TARGETS = TARGETS[FEATURES_LOOKBACK:-targets_lookback]
        TARGETS = TARGETS[-len(FEATURES):]


def _createModel():
    """Seting up the model with keras"""

    from keras.models import Sequential  # lazy load...
    from keras.layers import LSTM, Dense  # lazy load...
    global MODEL

    MODEL = Sequential()
    MODEL.add(
        LSTM(
            HIDDEN_SIZE,
            input_shape=(
                BATCH_SIZE,
                FEATURES.shape[2]
            ),
            batch_input_shape=(
                BATCH_SIZE,
                FEATURES.shape[1],
                FEATURES.shape[2]
            ),
            return_sequences=True,
            # stateful=True
        )
    )
    # MODEL.add(
    #     LSTM(
    #         HIDDEN_SIZE,
    #         return_sequences=True,
    #         # stateful=True
    #     )
    # )
    # MODEL.add(
    #     LSTM(
    #         HIDDEN_SIZE,
    #         # stateful=True
    #     )
    # )
    MODEL.add(
        Dense(
            3,
            activation='softmax'
        )
    )

    MODEL.compile(
        loss='categorical_crossentropy',
        optimizer='adam',
        metrics=['accuracy']
    )


def train():
    """Fit the ´MODEL´"""

    log.debug("Train tendency")

    if MODEL is None:
        _createModel()

    # this return the history... could be ploted or something
    MODEL.fit(
        FEATURES, TARGETS,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        shuffle=False,
        verbose=modelHelper.getVerbose()
    )   # TODO: make this interuptible

    # score = MODEL.evaluate(
    #     FEATURES, TARGETS,
    #     batch_size=BATCH_SIZE,
    #     verbose=modelHelper.getVerbose()
    # )
    # log.debug("score:", score)


def save():
    """Save the ´MODEL´ to ´conf.MODEL_TENDENCY_FILE´"""

    MODEL.save(conf.MODEL_TENDENCY_FILE)


def load():
    """Load the ´MODEL´ saved in ´conf.MODEL_TENDENCY_FILE´"""

    global MODEL
    if MODEL is None:
        from keras.models import load_model  # lazy load...
        MODEL = load_model(conf.MODEL_TENDENCY_FILE)


def _mergeCategories(arr):
    """TODO: we could use a generic function for all models"""

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

    return _mergeCategories(MODEL.predict_proba(
        X,
        batch_size=BATCH_SIZE,
        # verbose=modelHelper.getVerbose()
    ))


def getMergedTargets():
    """Return ´TARGETS´ in the same format than predict()"""

    if TARGETS is None or len(TARGETS) != len(FEATURES):
        return None

    return _mergeCategories(TARGETS)
