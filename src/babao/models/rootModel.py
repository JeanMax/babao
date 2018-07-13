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
from babao.models.tree.tendencyModel import TendencyModel
from babao.utils.enum import ActionEnum, CryptoEnum, cryptoAndActionTotrade

# import babao.models.models.tendency as tendency
# import babao.models.models.qlearn as qlearn
# import babao.models.tree.macdModel as macd

MIN_PROBA = 1e-2


class RootModel(ABCModel):
    """TODO"""

    dependencies_class = [
        TendencyModel,
        ExtremaModel,
    ]
    need_training = False

    def predict(self, since):
        """TODO"""

        for model in self.dependencies:  # debug loop
            pred_df = model.predict(since)
            pred_df = pd.DataFrame(
                (pred_df["buy"] - pred_df["sell"]).values, columns=["action"]
            )
            last_pred = pred_df.iat[-1, 0]
            log.debug(
                model.__class__.__name__, "prediction:",
                du.toStr(du.getTime()),
                last_pred, ActionEnum(round(last_pred))
            )

        pred_df = (
            (pred_df < -MIN_PROBA).astype(int).replace(1, ActionEnum.SELL.value)
            + (pred_df > MIN_PROBA).astype(int).replace(1, ActionEnum.BUY.value)
        ).replace(0, ActionEnum.HODL.value)
        return cryptoAndActionTotrade(CryptoEnum.XBT.value, pred_df)

    def plot(self, since):
        """TODO"""
        pass

    def train(self, since):
        """TODO"""
        pass

    def save(self):
        """TODO"""
        pass

    def load(self):
        """TODO"""
        pass
