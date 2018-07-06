"""
TODO
Buy/Sell strategy

This whole shit is temporary, don't worry
"""

import pandas as pd

from babao.models.modelBase import ABCModel
from babao.models.tree.extremaModel import ExtremaModel
from babao.utils.enum import ActionEnum, CryptoEnum, cryptoAndActionTotrade

# import babao.models.models.tendency as tendency
# import babao.models.models.qlearn as qlearn
# import babao.models.tree.macdModel as macd

MIN_PROBA = 1e-2


class RootModel(ABCModel):
    """TODO"""

    dependencies = [
        ExtremaModel,
    ]
    needTraining = False

    def predict(self, since):
        """TODO"""
        extrema = self.dependencies[0]
        pred_df = extrema.predict(since)
        pred_df = pd.DataFrame(
            (pred_df["buy"] - pred_df["sell"]).values, columns=["action"]
        )
        pred_df = (
            (pred_df < -MIN_PROBA).replace(True, ActionEnum.SELL)
            | (pred_df > MIN_PROBA).replace(True, ActionEnum.BUY)
        ).replace(False, ActionEnum.HODL.value)
        return cryptoAndActionTotrade(CryptoEnum.XBT.value, pred_df)

    def getPlotData(self, since):
        """TODO"""
        return self.dependencies[0].getPlotData(since)

    def _train(self, since):
        """TODO"""
        pass

    def _save(self):
        """TODO"""
        pass

    def _load(self):
        """TODO"""
        pass
