"""
Do you even lift bro?

The idea here is to give a common interface to all the models
so you can use these wrappers to call all of them at once.
TODO
"""

from multiprocessing.dummy import Pool as ThreadPool

import babao.utils.log as log
import babao.utils.file as fu
import babao.models.modelBase as mb
import babao.inputs.ledger.ledgerManager as lm
from babao.utils.enum import CryptoEnum

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
    for i, unused_var in enumerate(fetched_data):
        mb.INPUTS[i].write(fetched_data[i])


def plotModels(since):
    """
    Plot all models
    TODO
    """

    mb.MODELS[0].getPlotData(since).plot()


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
    rootModel = mb.MODELS[0]
    action_enum = rootModel.predict(since)
    # TODO: do not hardcode crypto_enum
    return lm.buyOrSell(action_enum, CryptoEnum.XBT)
