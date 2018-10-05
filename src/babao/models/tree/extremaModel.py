"""
The idea of that model is to find local extrema,
then classify them as minimum/nop/maximum (-1/0/1)
using a knn classifier (sklearn)
"""

import joblib  # just use pickle instead?
import pandas as pd
# import numpy as np
# from scipy import optimize

from sklearn import neighbors
# from sklearn import svm
# from sklearn import tree
# from sklearn import neural_network
# from sklearn import preprocessing

import babao.utils.indicators as indic
import babao.utils.log as log
import babao.utils.date as du
from babao.inputs.trades.krakenTradesInput import KrakenTradesXXBTZEURInput
from babao.models.modelBase import ABCModel
from babao.utils.scale import Scaler

LOOKBACK = 6  # TODO: nice one
Y_LABELS = ["buy", "hold", "sell"]


def _getTradeData(kraken_trades_input, since):
    """
    Read the necessary data from inputs, and start feature preparation

    It is important to keep the the returned data constant, as it is shared
    across the different models
    """
    trade_data = kraken_trades_input.read(since=since)
    log.debug(
        "Read data from", du.toStr(trade_data.index[0]),
        "to", du.toStr(trade_data.index[-1])
    )
    trade_data = kraken_trades_input.resample(trade_data)
    log.debug(
        "Resampled data from", du.toStr(trade_data.index[0]),
        "to", du.toStr(trade_data.index[-1])
    )
    trade_data = trade_data.loc[:, ["vwap", "volume"]]
    trade_data["vwap"] = Scaler().scaleFit(trade_data["vwap"])
    trade_data["volume"] = Scaler().scaleFit(trade_data["volume"])
    return trade_data


def _prepareFeatures(trade_data):
    """Prepare features for train/predict"""
    indic_data = indic.get(trade_data, [
        "sma_vwap_9", "sma_vwap_26", "sma_vwap_77",
        "sma_volume_26", "sma_volume_77",
    ]).dropna()
    return indic_data


def _prepareTargets(trade_data, lookback):
    """
    Prepare targets for train/predict
    Return a serie with values -1 (minimum), 0 (nop), or 1 (maximum)
    """
    prices = trade_data["vwap"]
    rev_prices = prices[::-1]

    return (
        (  # min forward & backward
            (prices.rolling(lookback).min() == prices)
            & ((rev_prices.rolling(lookback).min() == rev_prices)[::-1])
        ).astype(int).replace(1, -1)  # minima set to -1
    ) | (  # max forward & backward
        (prices.rolling(lookback).max() == prices)
        & ((rev_prices.rolling(lookback).max() == rev_prices)[::-1])
    ).astype(int).values  # maxima set to +1


class ExtremaModel(ABCModel):
    """A stupid simple model finding local extrema"""

    dependencies_class = [KrakenTradesXXBTZEURInput]
    need_training = True

    def _prepare(self, since, with_targets=False):
        """
        Prepare features and eventually targets (if ´with_targets´ is True)
        from the given ´since´ timestamp
        """
        trade_data = _getTradeData(self.dependencies[0], since)
        features = _prepareFeatures(trade_data)
        if not with_targets:
            return features
        targets = _prepareTargets(trade_data, LOOKBACK)
        targets = targets[-len(features):]  # compensate features.dropna()
        targets = targets[LOOKBACK:-LOOKBACK]  # remove un-label'd data
        features = features[LOOKBACK:-LOOKBACK]
        return features, targets

    def train(self, since):
        log.debug("Train extrema")
        features, targets = self._prepare(since, with_targets=True)
        self.model.fit(features, targets)
        return self.model.score(features, targets)

    def predict(self, since):
        features = self._prepare(since)
        pred = self.model.predict_proba(features)
        return pd.DataFrame(pred, columns=Y_LABELS, index=features.index)

    def plot(self, since):
        features, targets = self._prepare(since, with_targets=True)
        pred = self.model.predict_proba(features)
        pred_df = pd.DataFrame(pred, columns=Y_LABELS, index=features.index)
        plot_data = features.loc[:, ["vwap", "volume"]]
        plot_data["predict"] = pred_df["sell"] - pred_df["buy"]
        plot_data["target"] = targets.values / 3
        du.toDatetime(plot_data)
        plot_data.plot(title="Model Extrema")

    def save(self):
        joblib.dump(self.model, self.model_file)

    def load(self):
        try:
            self.model = joblib.load(self.model_file)
        except OSError:
            self.model = neighbors.KNeighborsClassifier(
                n_neighbors=3,
                weights="distance"
            )
