"""In this model we'll use q-learning to optimize buy/sell actions"""

import numpy as np
import pandas as pd

import babao.utils.log as log
import babao.config as conf
import babao.data.indicators as indic
import babao.data.ledger as ledger
import babao.strategy.modelHelper as modelHelper

MODEL = None
FEATURES = None

FEATURES_LOOKBACK = 0  # TODO

REQUIRED_COLUMNS = [
    "vwap",  # "volume",
    # "high", "low",
    "close",  # "open",
]
INDICATORS_COLUMNS = [
    "SMA_vwap_9", "SMA_vwap_26", "SMA_vwap_77", "SMA_vwap_167",
    # "SMA_volume_9", "SMA_volume_26", "SMA_volume_77",
]

BUY = 0
HOLD = 1
SELL = 2
NUM_ACTIONS = 3  # [buy, hold, sell]

MIN_BAL = 50  # maximum drawdown

ALPHA = 0.1  # learning rate
EPSILON = 0.1  # exploration  # TODO: decrement?
GAMMA = 0.9  # discount (1: long-term reward; 0: current-reward)
XP = []
MAX_XP = 10000

BATCH_SIZE = 1
HIDDEN_SIZE = 100
EPOCHS = 100


def prepare(full_data, train_mode=False):
    """
    Prepare features and targets for training (copy)

    ´full_data´: cf. ´prepareModels´
    """

    # TODO: use another dim for this, not more columns (3d)
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
    FEATURES["SMA_9-26"] = FEATURES["SMA_vwap_9"] - FEATURES["SMA_vwap_26"]
    FEATURES["MACD_9_26_10"] = indic.SMA(FEATURES["SMA_9-26"], 10)
    FEATURES["SMA_26-77"] = FEATURES["SMA_vwap_26"] - FEATURES["SMA_vwap_77"]
    FEATURES["MACD_26_77_10"] = indic.SMA(FEATURES["SMA_26-77"], 10)
    FEATURES = _addLookbacks(FEATURES, FEATURES_LOOKBACK)
    FEATURES = _reshape(FEATURES.values)

    global MAX_XP
    MAX_XP = len(FEATURES) * NUM_ACTIONS

    train_mode = train_mode  # unused...


def _getReward(price, next_price):
    """
    Return a reward (between 1 and -1)
    based on the performance of the previous action
    """

    bal = ledger.BALANCE["crypto"] * price + ledger.BALANCE["quote"]
    next_bal = ledger.BALANCE["crypto"] * next_price + ledger.BALANCE["quote"]
    # reward = (next_price - price) / price - (next_bal - bal) / bal

    reward = next_bal - bal

    # log.debug("reward:", reward) # DEBUG

    if reward > 1:
        return 1
    if reward < 1:
        return -1
    return reward


def _buyOrSell(action, price):
    """
    Apply the given action (if possible)

    TODO: this is very similar to strategy.strategy._buyOrSell
    """

    if action == SELL and ledger.BALANCE["crypto"] > 0.001:
        # log.info(
        #     "Sold for "
        #     + str(ledger.BALANCE["crypto"])
        #     + " crypto @ "
        #     + str(price)
        # )
        ledger.logSell(
            ledger.BALANCE["crypto"],
            price,
            crypto_fee=ledger.BALANCE["crypto"] / 100  # 1% fee
        )

    elif action == BUY and ledger.BALANCE["quote"] > 0.001:
        # log.info(
        #     "Bought for "
        #     + str(ledger.BALANCE["quote"])
        #     + " quote @ "
        #     + str(price)
        # )
        ledger.logBuy(
            ledger.BALANCE["quote"],
            price,
            quote_fee=ledger.BALANCE["quote"] / 100  # 1% fee
        )


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

    # TODO: ALPHA
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
            NUM_ACTIONS
        )
    )
    MODEL.compile(sgd(lr=.1), "sigmoid")


def train():
    """Train"""

    # X_len = len(FEATURES)  # TODO (needed in _gameOver)
    def _gameOver(index, price):
        """Check if an epoch is over"""

        # if index == X_len:
        #     return True
        if ledger.BALANCE["crypto"] * price + ledger.BALANCE["quote"] \
           < MIN_BAL:
            return True
        return False

    if MODEL is None:
        _createModel()
    ledger.setLog(False)  # we just want the final balance

    for e in range(EPOCHS):
        loss = 0.
        rewardTotal = 0
        price = -42
        feature = None
        game_over = False
        ledger.initBalance({"crypto": 0, "quote": 100})

        for i, next_feature in enumerate(FEATURES):
            if feature is None:
                feature = next_feature
                continue

            price = modelHelper.unscale(feature[0][0])
            game_over = _gameOver(i, price)
            if np.random.rand() <= EPSILON:
                action = np.random.randint(0, NUM_ACTIONS, 1)[0]
            else:
                action = np.argmax(
                    MODEL.predict(
                        np.array(feature),
                        batch_size=BATCH_SIZE,
                        # verbose=modelHelper.getVerbose()
                    )[0]  # expected reward
                )
            _buyOrSell(action, price)

            reward = _getReward(price, modelHelper.unscale(next_feature[0][0]))
            rewardTotal += reward

            _saveExperience([feature, action, reward, next_feature, game_over])
            inputs, targets = _getBatch()
            loss += MODEL.train_on_batch(inputs, targets)

            feature = next_feature
            if game_over:
                # log.warning("game over:", i)
                break

        score = ledger.BALANCE["crypto"] * price + ledger.BALANCE["quote"]
        hodl = price / modelHelper.unscale(FEATURES[0][0][0]) * 100
        log.debug(
            "Epoch", str(e + 1) + "/" + str(EPOCHS),
            # "-", str(round((tick - tack) / 1e9, 1)) + "s",
            "- loss:", round(loss, 4),
            "- rewardTotal:", round(rewardTotal, 4),
            "- score:", int(score - hodl),
            "(" + str(int(score)) + "-" + str(int(hodl)) + ")"
        )


def save():
    """Save the ´MODEL´ to ´conf.MODEL_QLEARN_FILE´"""

    # TODO: save experiences?
    MODEL.save(conf.MODEL_QLEARN_FILE)


def load():
    """Load the ´MODEL´ saved in ´conf.MODEL_QLEARN_FILE´"""

    global MODEL
    if MODEL is None:
        from keras.models import load_model  # lazy load...
        MODEL = load_model(conf.MODEL_QLEARN_FILE)


def _mergeCategories(arr):
    """TODO: we could use a generic function for all models"""

    df = pd.DataFrame(arr, columns=["buy", "hold", "sell"])
    return (df["sell"] - df["buy"]).values


def predict(X=None):
    """
    Call predict on the current ´MODEL´

    Format the result as values between -1 (buy) and 1 (sell))
    """

    # TODO: or just this? np.argmax(MODEL.predict(X))
    if X is None:
        X = FEATURES

    if len(X) == 1:
        X = np.array([X])

    return _mergeCategories(MODEL.predict_proba(
        np.reshape(X, (X.shape[0], X.shape[2])),
        batch_size=X.shape[0],
        # verbose=modelHelper.getVerbose()
    ))
