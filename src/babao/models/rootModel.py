"""
TODO
Buy/Sell strategy

This whole shit is temporary, don't worry
"""

import pandas as pd

import babao.utils.log as log
import babao.utils.date as du
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
        last_pred = pred_df.iat[-1, 0]
        log.debug(
            "rootModel prediction:",
            pd.to_datetime(du.getTime(), unit="ns"),
            last_pred, ActionEnum(round(last_pred))
        )
        pred_df = (
            (pred_df < -MIN_PROBA).replace(True, ActionEnum.SELL.value)
            + (pred_df > MIN_PROBA).replace(True, ActionEnum.BUY.value)
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
