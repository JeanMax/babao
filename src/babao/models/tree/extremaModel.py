"""
The idea of that model is to find local extrema,
then classify them as minimum/nop/maximum (-1/0/1)
using a knn classifier (sklearn)

TODO
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

import babao.config as conf
import babao.utils.indicators as indic
import babao.utils.log as log
import babao.utils.date as du
from babao.inputs.trades.krakenTradesInput import KrakenTradesXXBTZEURInput
from babao.models.modelBase import ABCModel
from babao.utils.scale import Scaler

LOOKBACK = 47  # TODO: nice one
Y_LABELS = ["buy", "hold", "sell"]


def _getTradeData(kraken_trades_input, since):
    """TODO"""
    trade_data = kraken_trades_input.read(since=since)
    trade_data = kraken_trades_input.resample(trade_data)
    trade_data = trade_data.loc[:, ["vwap", "volume"]]
    trade_data["vwap"] = Scaler().scaleFit(trade_data["vwap"])
    trade_data["volume"] = Scaler().scaleFit(trade_data["volume"])
    # TODO: save scalers
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
    """TODO"""

    dependencies = [KrakenTradesXXBTZEURInput]
    need_training = True

    def predict(self, since):
        """TODO"""
        trade_data = _getTradeData(self.dependencies[0], since)
        features = _prepareFeatures(trade_data)
        pred_df = pd.DataFrame(
            self.knn.predict_proba(features),
            columns=Y_LABELS
        )
        pred_df.index = trade_data[-len(pred_df):].index
        return pred_df

    def train(self, since):
        """TODO"""
        log.debug("Train extrema")
        trade_data = _getTradeData(self.dependencies[0], since)
        features = _prepareFeatures(trade_data)
        targets = _prepareTargets(trade_data, LOOKBACK)
        targets = targets[-len(features):]  # compensate features.dropna()
        features = features[LOOKBACK:-LOOKBACK]
        targets = targets[LOOKBACK:-LOOKBACK]
        self.knn.fit(features, targets)
        return self.knn.score(features, targets)

    def getPlotData(self, since):
        """TODO"""
        trade_data = _getTradeData(self.dependencies[0], since)
        features = _prepareFeatures(trade_data)
        targets = _prepareTargets(trade_data, LOOKBACK)
        targets = targets[-len(features):]  # compensate features.dropna()
        pred_df = pd.DataFrame(
            self.knn.predict_proba(features),
            columns=Y_LABELS
        )
        plot_data = features.loc[:, ["vwap", "volume"]]
        pred_df.index = plot_data.index
        plot_data["predict"] = pred_df["sell"] - pred_df["buy"]
        plot_data["target"] = targets.values / 3
        du.toDatetime(plot_data)
        return plot_data

    def save(self):
        """TODO"""
        joblib.dump(self.knn, conf.MODEL_EXTREMA_FILE)  # TODO: file

    # TODO: move to init?
    def load(self):
        """TODO"""
        try:
            self.knn = joblib.load(conf.MODEL_EXTREMA_FILE)
        except OSError:
            # TODO: k
            self.knn = neighbors.KNeighborsClassifier(
                n_neighbors=3,
                weights="distance"
            )
