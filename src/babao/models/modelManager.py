"""
Do you even lift bro?

The idea here is to give a common interface to all the models
so you can use these wrappers to call all of them at once.
TODO
"""

import babao.inputs.ledger.ledgerManager as lm
import babao.models.modelBase as mb
import babao.utils.enum as enu
import babao.utils.log as log


def plotModels(since):
    """
    Plot all models
    TODO
    """
    rootModel = mb.MODELS[0]
    rootModel.getPlotData(since).plot(title="root")


def trainModels(since):
    """
    Train all models and save the awesome result
    TODO
    """
    for model in mb.MODELS:
        if model.needTraining:
            score = model.train(since)
            log.debug("Score:", score)
            if score:
                log.info("Saving model")
                model.save()


def predictModelsMaybeTrade(since):
    """
    TODO
    """
    # TODO: break if inputs are out of sync
    rootModel = mb.MODELS[0]
    pred_df = rootModel.predict(since)
    trade_enum_val = pred_df.iat[-1, 0]
    if not trade_enum_val:
        return False
    return lm.buyOrSell(
        enu.ActionEnum(enu.tradeToAction(trade_enum_val)),
        enu.CryptoEnum(enu.tradeToCrypto(trade_enum_val))
    )
