"""Commands launched by parseArgv"""

import time
import os
import signal
import numpy as np
import pandas as pd

import babao.utils.log as log
import babao.utils.date as du
import babao.config as conf
import babao.strategy.transaction as tx
import babao.strategy.strategy as strat
import babao.strategy.modelManager as modelManager

from babao.inputs.kraken.krakenTradesInput import KrakenTradesXXBTZEURInput

K = None

EXIT = 0
TICK = None
LOCK = None

TRAIN_SET_LEN = 850  # TODO: config-var?
TEST_SET_LEN = 850  # TODO: config-var?
NUMBER_OF_TRAIN_SETS = 36  # TODO: config-var?


def _signalHandler(signal_code, unused_frame):
    """Catch signal INT/TERM, so we won't exit while playing with data files"""

    global EXIT
    EXIT = 128 + signal_code


def _delay(block=True):
    """
    Sleep the min amount of time required to still be friend with the api

    Also handle a lock to avoid having the graph read data while we write
    Return False if a signal have been caught (you need to exit).
    """

    if EXIT:
        return False

    if LOCK:
        try:
            LOCK.release()
        except ValueError:
            pass

    global TICK
    if TICK is not None:
        delta = time.time() - TICK
        log.debug("Loop took " + str(round(delta, 3)) + "s")
    else:
        delta = 0

    delta = 3 - delta  # TODO: define API_DELAY
    if delta > 0:
        time.sleep(delta)
    TICK = time.time()

    if LOCK:
        if delta < 0:
            time.sleep(1)  # TODO: workaround: graph need time
        LOCK.acquire(block=block)

    return not bool(EXIT)


def _launchGraph():
    """Start the graph process"""

    # we import here, so matplotlib can stay an optional dependency
    from multiprocessing import Process, Lock
    import babao.graph as graph

    global LOCK
    LOCK = Lock()
    p = Process(
        target=graph.initGraph,
        args=(LOCK,),
        name="babao-graph",
        daemon=True  # so we don't have to terminate it
    )
    p.start()
    time.sleep(0.5)  # TODO: define LIL_DELAY_JUST_IN_CASE
    LOCK.acquire()


def _initCmd(graph=False, simulate=True):
    """
    Generic command init function

    Init: signal handlers, api key, graph
    """

    signal.signal(signal.SIGINT, _signalHandler)
    signal.signal(signal.SIGTERM, _signalHandler)

    global K
    K = KrakenTradesXXBTZEURInput()

    tx.initLedger(simulate)

    if graph:
        _launchGraph()

    modelManager.loadModels()


def _getData():
    """Return the whole dataset splitted in two parts: (train, test)"""

    full_data = K.read()
    return full_data[:-TEST_SET_LEN], full_data[-TEST_SET_LEN:]


def wetRun(args):
    """Dummy"""
    _initCmd(args.graph, simulate=False)
    print("Sorry, this is not implemented yet :/")


def dryRun(args):
    """Real-time bot simulation"""

    _initCmd(args.graph)

    while True:
        K.write()
        # TODO:  do not hardcode the lookback
        fresh_data = K.read(since=du.nowMinus(weeks=1))
        if not fresh_data.empty:
            modelManager.prepareModels(fresh_data)
            timestamp = fresh_data.index[-1]
            price = fresh_data.at[timestamp, "close"]
            strat.analyse(
                feature_index=-1,  # there should be only one feature
                price=price,
                timestamp=timestamp
            )

        if not _delay():
            return


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

    while True:
        K.write()
        log.debug(
            "Fetched data till " + pd.to_datetime(K.last_row.name, unit="ns")
        )
        if not _delay():
            return


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
        if EXIT:
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
        while _delay(block=False):
            pass


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
