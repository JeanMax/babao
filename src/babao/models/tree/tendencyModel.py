"""
The idea of that model is to find local extrema,
then classify them as 0 (hold), 1 (sell), 2 (buy)
using a lstm neural network (keras)
"""

import numpy as np
import pandas as pd

from keras.models import Sequential, load_model
from keras.layers import LSTM, Dense, Flatten
from keras.utils.np_utils import to_categorical

import babao.utils.indicators as indic
import babao.utils.log as log
import babao.utils.date as du
from babao.utils.scale import Scaler
from babao.inputs.trades.krakenTradesInput import KrakenTradesXXBTZEURInput
import babao.models.modelBase as mb

FEATURES_LOOKBACK = 0  # TODO: nice one
TARGETS_LOOKBACK = 47  # TODO: idem
# (there is something to "_optimizeTargets" somewhere in the git history :o)

Y_LABELS = ["hold", "sell", "buy"]

HIDDEN_SIZE = 32
BATCH_SIZE = 1
EPOCHS = 10

MIN_PROBA = 0.1  # TODO


def _getTradeData(kraken_trades_input, since):
    """
    Read the necessary data from inputs, and start feature preparation

    It is important to keep the the returned data constant, as it is shared
    across the different models
    """
    trade_data = kraken_trades_input.read(since=since)
    trade_data = kraken_trades_input.resample(trade_data)
    cols = ["open", "high", "low", "close", "vwap", "volume"]
    trade_data = trade_data.loc[:, cols]
    cols.pop(-1)  # volume
    trade_data.loc[:, cols] = Scaler().scaleFit(trade_data.loc[:, cols])
    trade_data["volume"] = Scaler().scaleFit(trade_data["volume"])
    return trade_data


def _prepareFeatures(trade_data, lookback):
    """Prepare features for train/predict"""
    features = indic.get(trade_data.copy(), [
        "sma_vwap_9", "sma_vwap_26", "sma_vwap_77",
        "sma_volume_9", "sma_volume_26", "sma_volume_77",
        "macd_vwap_9_26_10", "macd_vwap_26_77_10"
    ]).dropna()
    features = mb.addLookbacks(features, lookback)
    return features


def _prepareTargets(trade_data, lookback):
    """
    Prepare targets for training
    0 (nop), 1 (sell), 2 (buy)
    """
    # rev = trade_data["vwap"][::-1]
    # rev_targets = (
    #     (rev.rolling(lookback).min() == rev).astype(int).replace(1, 2)
    #     | (rev.rolling(lookback).max() == rev).astype(int)
    # ).replace(3, 0)
    # return rev_targets[::-1]
    prices = trade_data["vwap"]
    rev_prices = prices[::-1]
    return (
        (  # min forward & backward
            (prices.rolling(lookback).min() == prices)
            & ((rev_prices.rolling(lookback).min() == rev_prices)[::-1])
        ).astype(int).replace(1, 2)  # minima set to 2
    ) | (  # max forward & backward
        (prices.rolling(lookback).max() == prices)
        & ((rev_prices.rolling(lookback).max() == rev_prices)[::-1])
    ).astype(int).values  # maxima set to +1


def _createModel(features_shape):
    """Create and compile a keras lstm model"""
    model = Sequential()
    model.add(
        LSTM(
            HIDDEN_SIZE,
            input_shape=(
                BATCH_SIZE,
                features_shape[2]
            ),
            batch_input_shape=(
                BATCH_SIZE,
                features_shape[1],
                features_shape[2]
            ),
            return_sequences=True,
            # stateful=True
        )
    )
    model.add(Flatten())  # TODO: workaround the batch/input shape is fucked up
    # model.add(
    #     LSTM(
    #         HIDDEN_SIZE,
    #         return_sequences=True,
    #         # stateful=True
    #     )
    # )
    # model.add(
    #     LSTM(
    #         HIDDEN_SIZE,
    #         # stateful=True
    #     )
    # )
    model.add(
        Dense(
            len(Y_LABELS),
            activation='softmax'
        )
    )
    model.compile(
        loss='categorical_crossentropy',
        optimizer='adam',
        metrics=['accuracy']
    )
    return model


class TendencyModel(mb.ABCModel):
    """A variant of the extrema model, using an lstm network"""

    dependencies_class = [KrakenTradesXXBTZEURInput]
    need_training = True

    def _prepare(self, since, with_targets=False):
        """
        Prepare features and eventually targets (if ´with_targets´ is True)
        from the given ´since´ timestamp
        """
        trade_data = _getTradeData(self.dependencies[0], since)
        features = _prepareFeatures(trade_data, FEATURES_LOOKBACK)
        if not with_targets:
            return features
        targets = _prepareTargets(trade_data, TARGETS_LOOKBACK)
        features = features[:-TARGETS_LOOKBACK]  # remove un-label'd data
        targets = targets[FEATURES_LOOKBACK:-TARGETS_LOOKBACK]
        targets = targets[-len(features):]  # compensate features.dropna()
        return features, targets

    def _score(self, since):
        """Score our pretty model"""
        features, targets = self._prepare(since, with_targets=True)
        pred = self.model.predict_proba(
            mb.reshape(features.values),
            batch_size=BATCH_SIZE
        )
        df = pd.DataFrame(pred, columns=Y_LABELS, index=features.index)
        df["predict"] = df["sell"] - df["buy"]
        del df["sell"]
        del df["buy"]
        df["target"] = targets.replace(2, -1).values

        score_table = {}
        granu = 100
        for min_proba in (i / granu for i in range(granu, 1, -1)):
            df["test"] = (
                (df["predict"] < -min_proba).astype(int).replace(1, -1)
                + (df["predict"] > min_proba).astype(int).replace(1, 1)
            )
            yay = df.loc[df["target"] == df["test"], "test"]
            score_table[min_proba] = len(yay) / len(df)
        score_table = sorted(score_table.items(), key=lambda k: k[1])
        # log.info(score_table)
        # TODO: save best proba
        return score_table[-1][1]

    def train(self, since):
        log.debug("Train tendency")
        features, targets = self._prepare(since, with_targets=True)
        features = mb.reshape(features.values)
        targets = to_categorical(targets.values)
        if self.model is None:
            self.model = _createModel(features.shape)
        self.model.fit(
            features, targets,
            epochs=EPOCHS,
            batch_size=BATCH_SIZE,
            shuffle=False,
            verbose=mb.getVerbose()
        )  # this return the history... could be ploted or something
        return self._score(since)
        # return self.model.evaluate(
        #     features, targets,
        #     batch_size=BATCH_SIZE,
        #     verbose=mb.getVerbose()
        # )

    def predict(self, since):
        features = self._prepare(since)
        reshaped_features = mb.reshape(features.values)
        if len(reshaped_features) == 1:
            reshaped_features = np.array([reshaped_features])
        pred = self.model.predict_proba(
            reshaped_features,
            batch_size=BATCH_SIZE,
            # verbose=mb.getVerbose()
        )
        return pd.DataFrame(pred, columns=Y_LABELS, index=features.index)

    def plot(self, since):
        features, targets = self._prepare(since, with_targets=True)
        pred = self.model.predict_proba(
            mb.reshape(features.values),
            batch_size=BATCH_SIZE
        )
        pred_df = pd.DataFrame(pred, columns=Y_LABELS, index=features.index)
        plot_data = features.loc[:, ["vwap"]]
        plot_data["predict"] = pred_df["sell"] - pred_df["buy"]
        plot_data["predict"] = plot_data.apply(
            lambda x: 0 if -MIN_PROBA < x.predict < MIN_PROBA else x.predict,
            axis=1
        )
        plot_data["target"] = targets.replace(2, -1).values / 3
        du.toDatetime(plot_data)
        plot_data.plot(title="Model Tendency")

    def save(self):
        self.model.save(self.model_file)

    def load(self):
        try:
            self.model = load_model(self.model_file)
        except OSError:
            self.model = None
