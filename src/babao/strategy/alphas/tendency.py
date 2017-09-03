"""
TODO
"""

import sklearn.preprocessing as prepro
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
SCALER = None
REQUIRED_COLUMNS = [
    "vwap", "volume"
]


# def addLookbacks(df, lookback=1):
#     for i in range(1, lookback + 1):
#         df["lookback_" + str(i)] = df["vwap"].shift(i)
#     return df.dropna()


def _prepareFeatures(full_data):
    """
    Prepare features for training (copy)

    ´full_data´: cf. ´prepareAlphas´
    """

    def _reshape(arr):
        """TODO"""

        return np.reshape(arr, (arr.shape[0], 1, arr.shape[1]))

    global SCALER
    global FEATURES
    # TODO: I'm unsure about this scaler
    SCALER = prepro.MinMaxScaler(feature_range=(0, 1))
    FEATURES = full_data.copy()

    for col in FEATURES.columns:
        if col not in REQUIRED_COLUMNS:
            del FEATURES[col]

    # FEATURES = preprocessing.normalize(FEATURES.values)
    FEATURES = SCALER.fit_transform(FEATURES.values)
    FEATURES = _reshape(FEATURES)


def _prepareTargets(full_data, lookback=100):
    """
    Prepare targets for training (copy)
    0 (nop), 1 (sell), 2 (buy)

    ´full_data´: cf. ´prepareAlphas´
    """

    global TARGETS

    rev = full_data["vwap"][::-1]
    TARGETS = kuti.to_categorical(
        (rev.rolling(lookback).min() == rev).astype(int).replace(1, 2)
        | (rev.rolling(lookback).max() == rev).astype(int)
    )[::-1]


def prepare(full_data, targets=False, lookback=100):
    """
    Prepare features and targets for training (copy)

    ´full_data´: cf. ´prepareAlphas´
    """

    _prepareFeatures(full_data)
    if targets:
        _prepareTargets(full_data, lookback)

        # TODO: handle rolling nan (in extrema too I guess)

        # global FEATURES
        # global TARGETS
        # FEATURES = FEATURES[:-lookback]
        # TARGETS = TARGETS[:-lookback]


def train():
    """Fit the ´MODEL´"""

    log.debug("Train tendency")

    global MODEL
    if MODEL is None:
        MODEL = kmod.Sequential()
        MODEL.add(klay.LSTM(16, input_shape=(1, len(REQUIRED_COLUMNS))))
        MODEL.add(klay.Dense(3, activation='softmax'))

        MODEL.compile(
            loss='categorical_crossentropy',
            optimizer='adam',
            metrics=['accuracy']
        )

    # this return the history... could be ploted or something
    MODEL.fit(
        FEATURES, TARGETS,
        epochs=10,
        batch_size=1,
        shuffle=False,
        verbose=2  # TODO: check verbose level for this
    )

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
