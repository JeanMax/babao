"""
Do you even lift bro?

The idea here is to give a common interface to all the models
so you can use these wrappers to call all of them at once.
TODO
"""

from multiprocessing.dummy import Pool as ThreadPool

import babao.inputs.ledger.ledgerManager as lm
import babao.models.modelBase as mb
import babao.utils.enum as enu
import babao.utils.file as fu
import babao.utils.log as log

POOL = None


def fetchDeps():
    """TODO: move?"""
    global POOL
    if POOL is None:
        POOL = ThreadPool(
            initializer=lambda x, y: [log.setLock(x), fu.setLock(y)],
            initargs=(log.LOCK, fu.LOCK)
        )
        # well educated people use to join & close pool
    fetched_data = POOL.map(lambda inp: inp.fetch(), mb.INPUTS)
    # TODO: catch if inputs are out of sync (then you need to stop predictModels)
    for i, _unused in enumerate(fetched_data):
        mb.INPUTS[i].write(fetched_data[i])


def plotModels(since):
    """
    Plot all models
    TODO
    """
    rootModel = mb.MODELS[0]
    rootModel.getPlotData(since).plot()


def trainModels(since):
    """
    Train all models and save the awesome result
    TODO
    """
    for model in mb.MODELS:
        model.train(since)


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
