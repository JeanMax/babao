"""
Root Model, base of the models tree
"""

import pandas as pd

import babao.utils.log as log
import babao.utils.date as du
from babao.models.modelBase import ABCModel
from babao.models.tree.qlearnModel import QlearnModel
# from babao.models.tree.extremaModel import ExtremaModel
# from babao.models.tree.tendencyModel import TendencyModel
# from babao.models.tree.macdModel import MacdModel
from babao.utils.enum import ActionEnum, CryptoEnum, cryptoAndActionTotrade

MIN_PROBA = 1e-2


class RootModel(ABCModel):
    """
    Root Model, base of the models tree

    Not modeling much, but handle the call of the dependencies predictions
    """

    dependencies_class = [
        # ExtremaModel,
        # TendencyModel,
        # MacdModel,
        QlearnModel
    ]
    need_training = False

    def predict(self, since):
        """Call predict on the dependencies, then somehow merge the results"""

        for model in self.dependencies:  # de-bug loop
            pred_df = model.predict(since)
            pred_df = pd.DataFrame(
                (pred_df["buy"] - pred_df["sell"]).values, columns=["action"]
            )
            last_pred = pred_df.iat[-1, 0]
            log.debug(
                model.__class__.__name__, "prediction:",
                du.toStr(du.TIME_TRAVELER.getTime()),
                last_pred, ActionEnum(round(last_pred))
            )

        pred_df = (
            (pred_df < -MIN_PROBA).astype(int).replace(1, ActionEnum.SELL.value)
            + (pred_df > MIN_PROBA).astype(int).replace(1, ActionEnum.BUY.value)
        ).replace(0, ActionEnum.HODL.value)
        return cryptoAndActionTotrade(CryptoEnum.XBT.value, pred_df)

    def plot(self, since):
        pass

    def train(self, since):
        pass

    def save(self):
        pass

    def load(self):
        pass
