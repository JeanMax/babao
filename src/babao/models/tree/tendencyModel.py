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
from babao.models.modelBase import ABCModel, getVerbose


FEATURES_LOOKBACK = 0  # TODO: nice one
TARGETS_LOOKBACK = 47  # TODO: idem
# (there is something to "_optimizeTargets" somewhere in the git history :o)

Y_LABELS = ["hold", "sell", "buy"]

HIDDEN_SIZE = 32
BATCH_SIZE = 1
EPOCHS = 5


def _getTradeData(kraken_trades_input, since):
    """TODO"""
    trade_data = kraken_trades_input.read(since=since)
    trade_data = kraken_trades_input.resample(trade_data)
    trade_data = trade_data.loc[:, ["vwap"]].copy()
    trade_data["vwap"] = Scaler().scaleFit(trade_data["vwap"])
    # trade_data["volume"] = Scaler().scaleFit(trade_data["volume"])
    # TODO: save scalers
    return trade_data


def _addLookbacks(df, look_back):
    """Add lookback(s) (shifted columns) to each df columns"""
    for i in range(1, look_back + 1):
        for col in df.columns:
            if "lookback" not in col:
                df[col + "_lookback_" + str(i)] = df[col].shift(i)
    return df.dropna()


def _reshape(arr):
    """Reshape the features to be keras-proof"""
    return np.reshape(arr, (arr.shape[0], 1, arr.shape[1]))


def _prepareFeatures(trade_data, lookback):
    """
    Prepare features for training (copy) TODO
    """
    features = indic.get(trade_data.copy(), [
        "sma_vwap_9", "sma_vwap_26", "sma_vwap_77", "sma_vwap_167",
        # "sma_volume_9", "sma_volume_26", "sma_volume_77",
        "macd_vwap_9_26_10", "macd_vwap_26_77_10"
    ]).dropna()
    features = _addLookbacks(features, lookback)
    return features
    # features = _reshape(features.values)  # TODO


def _prepareTargets(trade_data, lookback):
    """
    Prepare targets for training (copy)
    0 (nop), 1 (sell), 2 (buy)
    TODO
    """
    rev = trade_data["vwap"][::-1]
    rev_targets = (
        (rev.rolling(lookback).min() == rev).astype(int).replace(1, 2)
        | (rev.rolling(lookback).max() == rev).astype(int)
    ).replace(3, 0)
    return rev_targets[::-1]


def _createModel(features_shape):
    """TODO"""
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


class TendencyModel(ABCModel):
    """TODO"""

    dependencies_class = [KrakenTradesXXBTZEURInput]
    need_training = True

    def prepare(self, since, with_targets=False):
        """TODO"""
        trade_data = _getTradeData(self.dependencies[0], since)
        features = _prepareFeatures(trade_data, FEATURES_LOOKBACK)
        if not with_targets:
            return features
        targets = _prepareTargets(trade_data, TARGETS_LOOKBACK)
        features = features[:-TARGETS_LOOKBACK]  # remove un-label'd data
        targets = targets[FEATURES_LOOKBACK:-TARGETS_LOOKBACK]
        targets = targets[-len(features):]  # compensate features.dropna()
        return features, targets

    def train(self, since):
        """TODO"""
        log.debug("Train tendency")
        features, targets = self.prepare(since, with_targets=True)
        features = _reshape(features.values)
        targets = to_categorical(targets.values)
        if self.model is None:
            self.model = _createModel(features.shape)
        self.model.fit(
            features, targets,
            epochs=EPOCHS,
            batch_size=BATCH_SIZE,
            shuffle=False,
            verbose=getVerbose()
        )  # this return the history... could be ploted or something
        return self.model.evaluate(
            features, targets,
            batch_size=BATCH_SIZE,
            verbose=getVerbose()
        )

    def predict(self, since):
        """
        Format the result as values between -1 (buy) and 1 (sell))
        """
        features = self.prepare(since)
        features = _reshape(features.values)
        if len(features) == 1:
            features = np.array([features])
        pred = self.model.predict_proba(
            features,
            batch_size=BATCH_SIZE,
            # verbose=getVerbose()
        )
        return pd.DataFrame(pred, columns=Y_LABELS, index=features.index)

    def plot(self, since):
        """TODO"""
        features, targets = self.prepare(since, with_targets=True)
        pred = self.model.predict_proba(
            _reshape(features.values),
            batch_size=BATCH_SIZE
        )
        pred_df = pd.DataFrame(pred, columns=Y_LABELS, index=features.index)
        plot_data = features.loc[:, ["vwap"]]
        plot_data["predict"] = pred_df["sell"] - pred_df["buy"]
        plot_data["target"] = targets.replace(2, -1).values / 3
        du.toDatetime(plot_data)
        plot_data.plot(title="Model Tendency")

    def save(self):
        """TODO"""
        self.model.save(self.model_file)

    def load(self):
        """TODO"""
        try:
            self.model = load_model(self.model_file)
        except OSError:
            self.model = None
