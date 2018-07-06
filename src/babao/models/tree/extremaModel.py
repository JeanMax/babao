"""
The idea of that model is to find local extrema,
then classify them as minimum/nop/maximum (-1/0/1)
using a knn classifier (sklearn)

TODO
"""

# from sklearn.externals import joblib
import joblib  # just use pickle instead?
import pandas as pd
# import numpy as np
# from scipy import optimize
# from sklearn import preprocessing
from sklearn import neighbors

import babao.config as conf
import babao.utils.indicators as indic
import babao.utils.log as log
from babao.inputs.trades.krakenTradesInput import KrakenTradesXXBTZEURInput
from babao.models.modelBase import ABCModel
from babao.utils.scale import Scaler

# from sklearn import svm
# from sklearn import tree
# from sklearn import neural_network

LOOKBACK = 47  # TODO: nice one


def _getTradeData(krakenTradesInput, since):
    """TODO"""
    trade_data = krakenTradesInput.read(since=since)
    trade_data = krakenTradesInput.resample(trade_data)
    return trade_data[["vwap", "volume"]]


def _prepareFeatures(trade_data):
    """Prepare features for train/predict"""
    indic_data = indic.get(trade_data, [
        "SMA_vwap_9", "SMA_vwap_26", "SMA_vwap_77",
        "SMA_volume_26", "SMA_volume_77",
    ]).dropna()
    return Scaler().scale_fit(indic_data)  # TODO: save scaler


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
    needTraining = True

    def predict(self, since):
        """TODO"""
        trade_data = _getTradeData(self.dependencies[0], since)
        features = _prepareFeatures(trade_data)
        pred_df = pd.DataFrame(
            self.knn.predict_proba(features),
            columns=["buy", "hold", "sell"]
        )
        return pred_df

    def _train(self, since):
        """TODO"""
        log.debug("Train extrema")
        trade_data = _getTradeData(self.dependencies[0], since)
        features = _prepareFeatures(trade_data)
        targets = _prepareTargets(trade_data, LOOKBACK)
        targets = targets[-len(features):]  # compensate features.dropna()
        features = features[LOOKBACK:-LOOKBACK]
        targets = targets[LOOKBACK:-LOOKBACK]
        return self.knn.fit(features, targets)  # TODO: return score

    def getPlotData(self, since):
        """TODO"""
        trade_data = _getTradeData(self.dependencies[0], since)
        features = _prepareFeatures(trade_data)
        targets = _prepareTargets(trade_data, LOOKBACK)
        targets = targets[-len(features):]  # compensate features.dropna()
        pred_df = self.predict(since)  # TODO: don't double read/prepare
        plot_data = features
        plot_data["target"] = targets
        plot_data["predict"] = pred_df["sell"] - pred_df["buy"]
        return plot_data

    def _save(self):
        """TODO"""
        joblib.dump(self.knn, conf.MODEL_EXTREMA_FILE)  # TODO: file

    # TODO: move to init?
    def _load(self):
        """TODO"""
        try:
            self.knn = joblib.load(conf.MODEL_EXTREMA_FILE)
        except OSError:
            # TODO: k
            self.knn = neighbors.KNeighborsClassifier(
                n_neighbors=3,
                weights="distance"
            )
