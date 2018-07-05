"""
TODO
Buy/Sell strategy

This whole shit is temporary, don't worry
"""

# import babao.utils.log as log
# import babao.inputs.ledger.ledgerManager as lm
# from babao.utils.enum import CryptoEnum
from babao.models.modelBase import ABCModel
from babao.models.tree.extremaModel import ExtremaModel
# import babao.models.models.tendency as tendency
# import babao.models.models.qlearn as qlearn
# import babao.models.tree.macdModel as macd


class RootModel(ABCModel):
    """TODO"""

    dependencies = [
        ExtremaModel,
    ]
    needTraining = False

    def __init__(self):
        """TODO"""
        ABCModel.__init__(self)

    def predict(self, since):
        """TODO"""
        # extrema = self.dependencies[0]
        # pred_df = extrema.predict(since)
        raise NotImplementedError("TODO")
        # TODO: ugly workaround
        # avoid problems when the features are too short (lookback)
        # if (feature_index >= modelManager.FEATURES_LEN
        #         or modelManager.FEATURES_LEN <= 0):
        #     log.warning("models: feature_index out of range")
        #     return

        # TODO: 2d array if predict_proba
        # target = target_arr[0]  # TODO: merges model (decistion tree?)

        # if log.VERBOSE >= 4:
        #     log.debug("target:", target)

        # lm.buyOrSell(target, CryptoEnum.XBT)

    def _train(self, since):
        """TODO"""
        pass

    def _save(self):
        """TODO"""
        pass

    def _load(self):
        """TODO"""
        pass
