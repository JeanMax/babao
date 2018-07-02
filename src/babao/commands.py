"""Commands launched by parseArgv"""

import time
import os
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import Process, Lock
from prwlock import RWLock
import numpy as np
import pandas as pd


import babao.utils.signal as sig
import babao.utils.log as log
import babao.utils.date as du
import babao.utils.file as fu
import babao.config as conf
import babao.strategy.transaction as tx
import babao.strategy.strategy as strat
import babao.strategy.modelManager as modelManager

from babao.inputs.trades.krakenTradesInput import KrakenTradesXXBTZEURInput
from babao.inputs.trades.krakenTradesInput import KrakenTradesXETCZEURInput
from babao.inputs.trades.krakenTradesInput import KrakenTradesXETHZEURInput
from babao.inputs.trades.krakenTradesInput import KrakenTradesXLTCZEURInput
from babao.inputs.trades.krakenTradesInput import KrakenTradesXREPZEURInput
from babao.inputs.trades.krakenTradesInput import KrakenTradesXXLMZEURInput
from babao.inputs.trades.krakenTradesInput import KrakenTradesXXMRZEURInput
from babao.inputs.trades.krakenTradesInput import KrakenTradesXXRPZEURInput
from babao.inputs.trades.krakenTradesInput import KrakenTradesXZECZEURInput
from babao.inputs.trades.krakenTradesInput import KrakenTradesXXBTZCADInput
from babao.inputs.trades.krakenTradesInput import KrakenTradesXXBTZGBPInput
from babao.inputs.trades.krakenTradesInput import KrakenTradesXXBTZJPYInput
from babao.inputs.trades.krakenTradesInput import KrakenTradesXXBTZUSDInput

K = None

TRAIN_SET_LEN = 850  # TODO: config-var?
TEST_SET_LEN = 850  # TODO: config-var?
NUMBER_OF_TRAIN_SETS = 36  # TODO: config-var?


def _launchGraph():
    """Start the graph process"""

    # we import here, so matplotlib can stay an optional dependency
    import babao.graph as graph

    p = Process(
        target=graph.initGraph,
        args=(log.LOCK, fu.LOCK),
        name="babao-graph",
        daemon=True  # so we don't have to terminate it
    )
    p.start()


def _initCmd(graph=False, simulate=True):
    """
    Generic command init function

    Init: signal handlers, api key, graph
    """

    log.setLock(Lock())
    if graph:
        fu.setLock(RWLock())
    global K
    K = [
        KrakenTradesXXBTZEURInput(),
        KrakenTradesXETCZEURInput(),
        KrakenTradesXETHZEURInput(),
        KrakenTradesXLTCZEURInput(),
        KrakenTradesXREPZEURInput(),
        KrakenTradesXXLMZEURInput(),
        KrakenTradesXXMRZEURInput(),
        KrakenTradesXXRPZEURInput(),
        KrakenTradesXZECZEURInput(),
        KrakenTradesXXBTZCADInput(),
        KrakenTradesXXBTZGBPInput(),
        KrakenTradesXXBTZJPYInput(),
        KrakenTradesXXBTZUSDInput(),
    ]
    tx.initLedger(simulate)
    modelManager.loadModels()
    if graph:
        _launchGraph()
    sig.catchSignal()


def _getData():
    """Return the whole dataset splitted in two parts: (train, test)"""

    full_data = K[0].resample(K[0].read())
    return full_data[:-TEST_SET_LEN], full_data[-TEST_SET_LEN:]


def wetRun(args):
    """Dummy"""
    _initCmd(args.graph, simulate=False)
    print("Sorry, this is not implemented yet :/")


def dryRun(args):
    """Real-time bot simulation"""

    _initCmd(args.graph)
    pool = ThreadPool(
        initializer=lambda x, y: [log.setLock(x), fu.setLock(y)],
        initargs=(log.LOCK, fu.LOCK)
    )
    while not sig.EXIT:
        fetched_data = pool.map(lambda inp: inp.fetch(), K)
        for i, unused in enumerate(fetched_data):
            K[i].write(fetched_data[i])

        # TODO:  do not hardcode the lookback
        fresh_data = K[0].resample(K[0].read(since=du.nowMinus(weeks=1)))
        if not fresh_data.empty:
            modelManager.prepareModels(fresh_data)
            timestamp = fresh_data.index[-1]
            price = fresh_data.at[timestamp, "close"]
            strat.analyse(
                feature_index=-1,  # there should be only one feature
                price=price,
                timestamp=timestamp
            )
    pool.close()
    pool.join()


def fetch(args):
    """Fetch raw trade data since the beginning of times"""

    try:
        _initCmd(args.graph)
    except FileNotFoundError:
        log.warning("No model found.")

    for f in [conf.DB_FILE]:
        if os.path.isfile(f):
            # os.remove(f)  # TODO: warn user / create backup?
            log.warning("Database file already exists (" + f + ").")

    while not sig.EXIT:
        K[0].write(K[0].fetch())
        log.debug(
            "Fetched data till " + pd.to_datetime(K[0].last_row.name, unit="ns")
        )


def backtest(args):
    """
    Just a naive backtester

    It will call the trained strategies on each test data point
    """

    _initCmd(args.graph)

    big_fat_data = _getData()[1]
    modelManager.prepareModels(big_fat_data)
    big_fat_data_index = big_fat_data.index.values
    big_fat_data_prices = big_fat_data["close"].values
    del big_fat_data

    start_time = time.time()

    # pylint: disable=consider-using-enumerate
    for i in range(len(big_fat_data_index)):
        strat.analyse(
            feature_index=i,
            price=big_fat_data_prices[i],
            timestamp=big_fat_data_index[i]
        )
        if sig.EXIT:
            return

    price = big_fat_data_prices[-1]
    score = tx.L["crypto"].balance * price + tx.L["quote"].balance
    hodl = price / big_fat_data_prices[0] * 100
    log.info(
        "Backtesting done! Score: " + str(round(float(score)))
        + "% vs HODL: " + str(round(hodl)) + "%"
    )
    log.debug(
        "Backtesting took "
        + str(round(time.time() - start_time, 3)) + "s"
    )

    if args.graph:
        # TODO: exit if graph is closed
        while not sig.EXIT:
            time.sleep(0.1)


def train(args):
    """Train the various (awesome) algorithms"""

    # _initCmd(args.graph)

    train_data, test_data = _getData()

    splits_size = int(len(train_data) / TRAIN_SET_LEN)
    splits = np.array_split(train_data, splits_size)

    start = splits_size - NUMBER_OF_TRAIN_SETS
    if start < 0:
        start = 0
    for i in range(start, splits_size):
        log.debug(
            "Using train set", i + 1, "/", splits_size,
            "- set length:", len(splits[i])
        )

        modelManager.prepareModels(splits[i], train_mode=True)
        modelManager.trainModels()

        if args.graph:
            modelManager.plotModels(splits[i])

    if args.graph:
        modelManager.prepareModels(test_data, train_mode=False)
        modelManager.plotModels(test_data)

        import matplotlib.pyplot as plt
        plt.show()
