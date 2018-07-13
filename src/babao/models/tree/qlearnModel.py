"""In this model we'll use q-learning to optimize buy/sell actions"""

import numpy as np
import pandas as pd

import babao.config as conf
import babao.inputs.ledger.ledgerManager as lm
import babao.utils.indicators as indic
import babao.utils.log as log
from babao.utils.enum import CryptoEnum

MODEL = None
FEATURES = None
PREV_PRICE = None

BUY = 0
SELL = 1
NUM_ACTIONS = 2  # [buy, sell]

XP = []
MAX_XP = 10000

FEATURES_LOOKBACK = 48  # TODO

REQUIRED_COLUMNS = [
    "close",
    "vwap",
    "volume",
    # "high", "low",
    # "open",
]
INDICATORS_COLUMNS = [
    "sma_vwap_9", "sma_vwap_26", "sma_vwap_77",
    "sma_volume_9", "sma_volume_26", "sma_volume_77",
    "macd_vwap_9_26_10", "macd_vwap_26_77_10"
]

MIN_TRANSACTION_PERCENT = 5

ALPHA = 0.1  # learning rate
EPSILON = 0.1  # exploration
GAMMA = 0.9  # discount (1: long-term reward; 0: current-reward)

BATCH_SIZE = 1
HIDDEN_SIZE = 64
EPOCHS = 200


def prepare(full_data, train_mode=False):
    """
    Prepare features and targets for training (copy)

    ´full_data´: cf. ´prepareModels´
    """

    def _addLookbacks(arr):
        """
        Add lookback(s) (shifted columns) to each df columns
        Reshape the features to be keras-proof
        """

        res = None
        for i in range(len(arr) - FEATURES_LOOKBACK):
            if res is None:
                res = np.array([arr[i:i + FEATURES_LOOKBACK]])
            else:
                res = np.append(
                    res,
                    np.array([arr[i: i + FEATURES_LOOKBACK]]),
                    axis=0
                )
        return res

    global FEATURES
    FEATURES = full_data.copy()

    # TODO: same pattern in extrema.py
    for c in FEATURES.columns:
        if c not in REQUIRED_COLUMNS:
            del FEATURES[c]

    FEATURES = indic.get(FEATURES, INDICATORS_COLUMNS)
    FEATURES = modelHelper.scaleFit(FEATURES)
    FEATURES = _addLookbacks(FEATURES.dropna().values)

    global MAX_XP
    MAX_XP = FEATURES.shape[0] * NUM_ACTIONS * FEATURES.shape[2]

    train_mode = train_mode  # unused...


# TODO: use lm.buyOrSell instead
def _buyOrSell(action, price, index):
    """
    Apply the given action (if possible)

    Return a reward (between 1 and -1)
    based on the performance of the previous action
    """

    global PREV_PRICE
    reward = 0

    if action == SELL and lm.LEDGERS[CryptoEnum.XBT].balance > 0.001:
        # reward = (price - (PREV_PRICE + PREV_PRICE / 100)) / PREV_PRICE * 100
        if price > PREV_PRICE + PREV_PRICE * MIN_TRANSACTION_PERCENT / 100:
            reward = 1
        elif price > PREV_PRICE + PREV_PRICE / 100:
            reward = 0.1
        else:
            reward = -1
        lm.LEDGERS[conf.QUOTE].sell(
            lm.LEDGERS[CryptoEnum.XBT],
            lm.LEDGERS[CryptoEnum.XBT].balance,
            price,
            index
        )
        PREV_PRICE = price
    elif action == BUY and lm.LEDGERS[conf.QUOTE].balance > 0.001:
        if PREV_PRICE is not None:
            # reward = (PREV_PRICE - (price + price / 100)) / PREV_PRICE * 100
            if price < PREV_PRICE - PREV_PRICE * MIN_TRANSACTION_PERCENT / 100:
                reward = 1
            elif price < PREV_PRICE - PREV_PRICE / 100:
                reward = 0.1
            else:
                reward = -1
        lm.LEDGERS[conf.QUOTE].buy(
            lm.LEDGERS[CryptoEnum.XBT],
            lm.LEDGERS[conf.QUOTE].balance,
            price,
            index
        )
        PREV_PRICE = price

    if log.VERBOSE >= 4 and reward != 0:
        log.info("reward:", round(reward, 4))

    return reward


def _saveExperience(xp):
    """Save experiences < s, a, r, s’ > we make during gameplay"""

    global XP
    XP.append(xp)
    XP = XP[-MAX_XP:]


def _getBatch():
    """
    Get a random experience to train on

    We add the target using this pretty formula:
    (1 - alpha) * Q(s, a)  +  alpha * reward  +  gamma * max_a'Q(s', a')
    """

    feature, action, reward, next_feature, game_over = XP[
        np.random.randint(0, len(XP), BATCH_SIZE)[0]
    ]

    target = MODEL.predict(
        feature,
        batch_size=BATCH_SIZE,
        # verbose=modelHelper.getVerbose()
    )  # * (1 - ALPHA)

    target[0][action] = reward  # * ALPHA
    if not game_over:
        target[0][action] += GAMMA * np.max(MODEL.predict(
            next_feature,
            batch_size=BATCH_SIZE,
            # verbose=modelHelper.getVerbose()
        )[0])

    return feature, target


def _createModel():
    """Seting up the model with keras"""

    from keras.models import Sequential  # lazy load...
    from keras.layers import Dense  # lazy load...
    from keras.optimizers import sgd  # lazy load...
    global MODEL

    MODEL = Sequential()
    MODEL.add(
        Dense(
            HIDDEN_SIZE,
            input_shape=(FEATURES.shape[2], ),
            activation='relu'
        )
    )
    MODEL.add(
        Dense(
            HIDDEN_SIZE,
            activation='relu'
        )
    )
    MODEL.add(
        Dense(
            NUM_ACTIONS,
            # activation="sigmoid"
        )
    )

    MODEL.compile(
        sgd(lr=.1),
        loss="mse"
    )


def train():
    """Train"""

    if MODEL is None:
        _createModel()

    # TODO: move these?
    lm.LEDGERS[CryptoEnum.XBT].verbose = log.VERBOSE >= 4
    lm.LEDGERS[conf.QUOTE].verbose = log.VERBOSE >= 4

    for e in range(EPOCHS):
        loss = 0.
        reward_total = 0
        price = -42
        feature = None
        game_over = False
        lm.LEDGERS[CryptoEnum.XBT].balance = 0
        lm.LEDGERS[conf.QUOTE].balance = 100

        for i, next_feature in enumerate(FEATURES):
            if feature is None:
                feature = next_feature
                continue

            price = modelHelper.unscale(feature[-1][0])
            game_over = lm.gameOver()
            if np.random.rand() <= EPSILON - (e + 1) / EPOCHS * EPSILON:
                action = np.random.randint(0, NUM_ACTIONS, 1)[0]
            else:
                expected_reward = MODEL.predict(
                    feature,
                    batch_size=BATCH_SIZE,
                    # verbose=modelHelper.getVerbose()
                )[0]
                action = np.argmax(expected_reward)
                if log.VERBOSE >= 4:
                    log.info("expected_reward", expected_reward)

            reward = _buyOrSell(action, price, i)
            reward_total += reward

            _saveExperience([feature, action, reward, next_feature, game_over])
            inputs, targets = _getBatch()
            loss += MODEL.train_on_batch(inputs, targets)

            feature = next_feature
            if game_over:
                if log.VERBOSE >= 4:
                    log.warning("game over:", i, "/", len(FEATURES))
                break

        score = lm.getGlobalBalanceInQuote()
        hodl = price / modelHelper.unscale(FEATURES[0][-1][0]) * 100
        log.debug(
            "Epoch", str(e + 1) + "/" + str(EPOCHS),
            "- loss:", round(loss, 4),
            "- reward_total:", round(reward_total, 4),
            "- score:", int(score - hodl),
            "(" + str(int(score)) + "-" + str(int(hodl)) + ")"
        )


def save():
    """Save the ´MODEL´ to ´self.model_file´"""

    # TODO: save experiences?
    MODEL.save(self.model_file)


def load():
    """Load the ´MODEL´ saved in ´self.model_file´"""

    global MODEL
    if MODEL is None:
        from keras.models import load_model  # lazy load...
        MODEL = load_model(self.model_file)


def _mergeCategories(arr):
    """TODO: we could use a generic function for all models"""

    df = pd.DataFrame(arr, columns=["buy", "hold", "sell"])
    return (df["sell"] - df["buy"]).values


def predict(features=None):
    """
    Call predict on the current ´MODEL´

    Format the result as values between -1 (buy) and 1 (sell))
    """

    # TODO: or just this? np.argmax(MODEL.predict(features))
    if features is None:
        features = FEATURES

    if len(features) == 1:
        features = np.array([features])

    return _mergeCategories(MODEL.predict_proba(
        np.reshape(features, (features.shape[0], features.shape[2])),
        batch_size=features.shape[0],
        # verbose=modelHelper.getVerbose()
    ))
