"""
Simple macd based model,
with a very elegant algorithm (aka: brute-force)
"""

import pickle
import numpy as np
from sklearn.model_selection import ParameterGrid

import babao.config as conf
import babao.inputs.inputManager as im
import babao.inputs.ledger.ledgerManager as lm
from babao.inputs.trades.krakenTradesInput import KrakenTradesXXBTZEURInput
import babao.utils.date as du
import babao.utils.indicators as indic
import babao.utils.log as log
from babao.utils.scale import Scaler
from babao.utils.enum import CryptoEnum, ActionEnum
import babao.models.modelBase as mb

MIN_MACD = 1e-2


def _getTradeData(kraken_trades_input, since):
    """TODO"""
    trade_data = kraken_trades_input.read(since=since)
    trade_data = kraken_trades_input.resample(trade_data)
    trade_data = trade_data.loc[:, ["vwap"]]
    trade_data["vwap"] = Scaler().scaleFit(trade_data["vwap"])
    # trade_data["volume"] = Scaler().scaleFit(trade_data["volume"])
    # TODO: save scalers
    return trade_data


def _resetLedgers():
    """TODO"""
    lm.LEDGERS[CryptoEnum.XBT].balance = 0
    lm.LEDGERS[conf.QUOTE].balance = 100
    lm.LEDGERS[CryptoEnum.XBT].last_tx = 0
    lm.LEDGERS[conf.QUOTE].last_tx = 0


def _play(features):
    """Play an epoch with the given macd parameters"""

    time_base = features.index[0]
    now = time_base
    index = 0  # in case len(features) == 0
    for index, feature in enumerate(features.values):
        macd = feature[1]
        if np.isnan(macd):
            continue

        now += du.secToNano(index * conf.TIME_INTERVAL * 60)
        im.timeTravel(now)
        if macd < -MIN_MACD:
            lm.buyOrSell(ActionEnum.SELL, CryptoEnum.XBT)
        elif macd > MIN_MACD:
            lm.buyOrSell(ActionEnum.BUY, CryptoEnum.XBT)

        if lm.gameOver():
            # if log.VERBOSE >= 4:
            log.warning("game over:", index, "/", len(features))
            return -42

    score = lm.getGlobalBalanceInQuote()
    hodl = features["vwap"].iat[index] / features["vwap"].iat[0] * 100

    # if log.VERBOSE >= 4:
    log.debug(
        "score:", int(score - hodl),
        "(" + str(int(score)) + "-" + str(int(hodl)) + ")"
    )

    return score  # - hodl


def _playLoop(features, param_grid):
    """TODO"""
    now = du.getTime()
    param_grid_len = len(param_grid)

    for i, param in enumerate(param_grid):
        if param["fast_delay"] >= param["slow_delay"]:
            continue

        features["macd"] = indic.macd(
            features["vwap"],
            param["fast_delay"], param["slow_delay"], param["signal_delay"]
        )
        # if log.VERBOSE >= 4:
        log.debug(
            "Testing params:", param["fast_delay"],
            param["slow_delay"], param["signal_delay"]
        )

        _resetLedgers()
        param["score"] = _play(features)

        percent = i / param_grid_len * 100
        if i and not bool(percent % 1):
            log.debug(
                str(int(percent)) + "% done",
                "- best yet:",
                sorted(param_grid, key=lambda k: k["score"])[-1]
            )

    im.timeTravel(now)
    return sorted(param_grid, key=lambda k: k["score"])


class MacdModel(mb.ABCModel):
    """TODO"""

    dependencies_class = [KrakenTradesXXBTZEURInput]
    need_training = True

    def prepare(self, since, with_macd=False):
        """TODO"""
        trade_data = _getTradeData(self.dependencies[0], since)
        if with_macd:
            trade_data["macd"] = indic.macd(
                trade_data["vwap"],
                self.model["fast_delay"],
                self.model["slow_delay"],
                self.model["signal_delay"]
            )
            trade_data.dropna(inplace=True)
        return trade_data

    def train(self, since):
        """TODO"""
        log.debug("Train macd")
        features = self.prepare(since)
        lm.LEDGERS[CryptoEnum.XBT].verbose = log.VERBOSE >= 4
        lm.LEDGERS[conf.QUOTE].verbose = log.VERBOSE >= 4

        param_grid = list(ParameterGrid({
            "fast_delay": range(9, 100, 1),
            "slow_delay": range(25, 200, 1),
            "signal_delay": range(10, 30, 1),
            # "fast_delay": [9],
            # "slow_delay": [26],
            # "signal_delay": [10],
            "score": [-42]
        }))

        sorted_param_grid = _playLoop(features, param_grid)
        log.debug("Top Ten:")
        for i in range(len(sorted_param_grid[-10:]), 0, -1):
            log.debug(sorted_param_grid[-i])

        self.model = sorted_param_grid[-1]
        score = self.model["score"]
        del self.model["score"]
        return score

    def predict(self, since):
        """
        Format the result as values between -1 (buy) and 1 (sell))
        """
        features = self.prepare(since, with_macd=True)
        macd = features["macd"]
        features["buy"] = (macd > MIN_MACD).astype(int)
        features["sell"] = (macd < -MIN_MACD).astype(int)
        features["hold"] = (features["buy"] + features["sell"] == 0).astype(int)
        pred_df = features.loc[:, ["hold", "sell", "buy"]]
        return pred_df

    def plot(self, since):
        """TODO"""
        plot_data = self.prepare(since, with_macd=True)
        pred_df = self.predict(since)
        plot_data["predict"] = pred_df["sell"] - pred_df["buy"]
        plot_data = plot_data.loc[:, ["vwap", "predict"]]
        du.toDatetime(plot_data)
        plot_data.plot(title="Model Macd")

    def save(self):
        """TODO"""
        with open(self.model_file, "wb") as f:
            pickle.dump(self.model, f)

    def load(self):
        """TODO"""
        try:
            with open(self.model_file, "rb") as f:
                self.model = pickle.load(f)
        except OSError:
            self.model = {
                "fast_delay": 46,
                "slow_delay": 75,
                "signal_delay": 22
            }
