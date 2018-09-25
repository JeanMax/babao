"""In this model we'll use q-learning to optimize buy/sell actions"""

import numpy as np
import pandas as pd

from keras.models import Sequential, load_model
from keras.layers import Dense
from keras.optimizers import sgd

import babao.config as conf
import babao.inputs.ledger.ledgerManager as lm
import babao.utils.indicators as indic
import babao.utils.log as log
import babao.utils.date as du
from babao.utils.enum import CryptoEnum
from babao.utils.scale import Scaler
from babao.inputs.trades.krakenTradesInput import KrakenTradesXXBTZEURInput
import babao.models.modelBase as mb

PREV_PRICE = None

BUY = 0
SELL = 1
NUM_ACTIONS = 3  # [buy, hold, sell]

FEATURES_LOOKBACK = 48

MIN_TRANSACTION_PERCENT = 5

ALPHA = 0.1  # learning rate
EPSILON = 0.1  # exploration
GAMMA = 0.9  # discount (1: long-term reward; 0: current-reward)

BATCH_SIZE = 1
HIDDEN_SIZE = 64
EPOCHS = 2


def _prepareFeatures(trade_data):
    """
    Prepare features for training (copy) TODO
    """
    features = indic.get(trade_data.copy(), [
        "sma_vwap_9", "sma_vwap_26", "sma_vwap_77",
        "sma_volume_9", "sma_volume_26", "sma_volume_77",
        "macd_vwap_9_26_10", "macd_vwap_26_77_10"
    ]).dropna()
    return features


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


def _createModel(features_shape):
    """Seting up the model with keras"""
    model = Sequential()
    model.add(
        Dense(
            HIDDEN_SIZE,
            input_shape=(features_shape[2], ),
            activation='relu'
        )
    )
    model.add(
        Dense(
            HIDDEN_SIZE,
            activation='relu'
        )
    )
    model.add(
        Dense(
            NUM_ACTIONS,
            activation="sigmoid"
        )
    )

    model.compile(
        sgd(lr=.1),
        loss="mse"
    )
    return model


def _mergeCategories(arr):
    """TODO: we could use a generic function for all models"""

    df = pd.DataFrame(arr, columns=["buy", "hold", "sell"])
    return (df["sell"] - df["buy"]).values


class QlearnModel(mb.ABCModel):
    """TODO"""

    dependencies_class = [KrakenTradesXXBTZEURInput]
    need_training = True

    def _saveExperience(self, xp):
        """Save experiences < s, a, r, s’ > we make during gameplay"""
        self.xp.append(xp)
        self.xp = self.xp[-self.max_xp:]

    def _getBatch(self):
        """
        Get a random experience to train on

        We add the target using this pretty formula:
        (1 - alpha) * Q(s, a)  +  alpha * reward  +  gamma * max_a'Q(s', a')
        """

        feature, action, reward, next_feature, game_over = self.xp[
            np.random.randint(0, len(self.xp), BATCH_SIZE)[0]
        ]

        target = self.model.predict(
            feature,
            batch_size=BATCH_SIZE,
            # verbose=mb.getVerbose()
        )  # * (1 - ALPHA)

        target[0][action] = reward  # * ALPHA
        if not game_over:
            target[0][action] += GAMMA * np.max(self.model.predict(
                next_feature,
                batch_size=BATCH_SIZE,
                # verbose=mb.getVerbose()
            )[0])

        return feature, target

    def _getTradeData(self, kraken_trades_input, since):
        """TODO"""
        trade_data = kraken_trades_input.read(since=since)
        trade_data = kraken_trades_input.resample(trade_data)
        cols = ["close", "vwap", "volume"]
        trade_data = trade_data.loc[:, cols]
        cols.pop(-1)  # volume
        self.price_scaler = Scaler()
        self.volume_scaler = Scaler()
        trade_data.loc[:, cols] = self.price_scaler.scaleFit(
            trade_data.loc[:, cols]
        )
        trade_data["volume"] = self.volume_scaler.scaleFit(
            trade_data["volume"]
        )
        return trade_data

    def prepare(self, since):
        """TODO"""
        trade_data = self._getTradeData(self.dependencies[0], since)
        features = _prepareFeatures(trade_data)
        features = mb.addLookbacks3d(
            features.dropna().values, FEATURES_LOOKBACK
        )
        return features

    def train(self, since):
        """TODO"""
        log.debug("Train qlearn")
        lm.LEDGERS[CryptoEnum.XBT].verbose = log.VERBOSE >= 4
        lm.LEDGERS[conf.QUOTE].verbose = log.VERBOSE >= 4

        features = self.prepare(since)
        self.xp = []
        self.max_xp = features.shape[0] * NUM_ACTIONS * features.shape[2]

        if self.model is None:
            self.model = _createModel(features.shape)

        for e in range(EPOCHS):
            loss = 0.
            reward_total = 0
            price = -42
            feature = None
            game_over = False
            lm.LEDGERS[CryptoEnum.XBT].balance = 0
            lm.LEDGERS[conf.QUOTE].balance = 100

            for i, next_feature in enumerate(features):
                if feature is None:
                    feature = next_feature
                    continue

                price = self.price_scaler.unscale(feature[-1][0])
                game_over = lm.gameOver()
                if np.random.rand() <= EPSILON - (e + 1) / EPOCHS * EPSILON:
                    action = np.random.randint(0, NUM_ACTIONS, 1)[0]
                else:
                    expected_reward = self.model.predict(
                        feature,
                        batch_size=BATCH_SIZE,
                        # verbose=mb.getVerbose()
                    )[0]
                    action = np.argmax(expected_reward)
                    if log.VERBOSE >= 4:
                        log.info("expected_reward", expected_reward)

                reward = _buyOrSell(action, price, i)
                reward_total += reward

                self._saveExperience(
                    [feature, action, reward, next_feature, game_over]
                )
                inputs, targets = self._getBatch()
                loss += self.model.train_on_batch(inputs, targets)

                feature = next_feature
                if game_over:
                    if log.VERBOSE >= 4:
                        log.warning("game over:", i, "/", len(features))
                    break

            score = lm.getGlobalBalanceInQuote()
            hodl = price / self.price_scaler.unscale(features[0][-1][0]) * 100
            log.debug(
                "Epoch", str(e + 1) + "/" + str(EPOCHS),
                "- loss:", round(loss, 4),
                "- reward_total:", round(reward_total, 4),
                "- score:", int(score - hodl),
                "(" + str(int(score)) + "-" + str(int(hodl)) + ")"
            )
        return score

    def predict(self, since):
        """
        Format the result as values between -1 (buy) and 1 (sell))
        """
        features = self.prepare(since)

        # TODO: or just this? np.argmax(self.model.predict(features))
        if len(features) == 1:
            features = np.array([features])
        return _mergeCategories(self.model.predict_proba(
            np.reshape(features, (features.shape[0], features.shape[2])),
            batch_size=features.shape[0],
            # verbose=mb.getVerbose()
        ))

    def plot(self, since):
        """TODO"""
        plot_data = self.prepare(since)
        pred_df = self.predict(since)
        plot_data["predict"] = pred_df["sell"] - pred_df["buy"]
        plot_data = plot_data.loc[:, ["vwap", "predict"]]
        du.toDatetime(plot_data)
        plot_data.plot(title="Model Qlearn")

    def save(self):
        """TODO"""
        self.model.save(self.model_file)

    def load(self):
        """TODO"""
        try:
            self.model = load_model(self.model_file)
        except OSError:
            self.model = None
