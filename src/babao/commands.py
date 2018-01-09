"""Commands launched by parseArgv"""

import time
import os
import signal
import numpy as np

import babao.utils.log as log
import babao.utils.file as fu
import babao.config as conf
import babao.api.api as api
import babao.data.resample as resamp
import babao.data.ledger as ledger
import babao.strategy.strategy as strat
import babao.strategy.trainer as trainer

EXIT = 0
TICK = None
LOCK = None

DATA_SET_LEN = 1000  # lenght of train/test data sets TODO: config-var?
NUMBER_OF_TRAIN_SETS = 1  # TODO: config-var?


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


def _initCmd(graph=False, simulate=False, with_api=True):
    """
    Generic command init function

    Init: signal handlers, api key, graph
    """

    signal.signal(signal.SIGINT, _signalHandler)
    signal.signal(signal.SIGTERM, _signalHandler)

    strat.initLastTransactionPrice()
    trainer.loadAlphas()

    if with_api:
        api.initKey()

    ledger.initBalance()
    if simulate and fu.getLastRows(conf.DB_FILE, conf.LEDGER_FRAME, 1).empty:
        ledger.logQuoteDeposit(100)

    if graph:
        _launchGraph()


def _getData():
    """Return the whole dataset splitted in two parts: (train, test)"""

    # with float < 64, smaller size but longer to process
    # (might be a cast issue somewhere else)
    full_data = resamp.resampleTradeData(
        fu.read(conf.DB_FILE, conf.TRADES_FRAME)
    )

    # TODO: we remove the head because there is not enough volume at first
    # full_data = full_data.tail(int(len(full_data) * 0.7))

    return full_data[:-DATA_SET_LEN], full_data[-DATA_SET_LEN:]


def wetRun(args):
    """Dummy"""
    print(repr(args))
    print("Sorry, this is not implemented yet :/")


def dryRun(args):
    """Real-time bot simulation"""

    _initCmd(args.graph, simulate=True)

    while True:
        api.dumpData()  # TODO: this could use a renaming

        # TODO:  do not hardcode the lookback
        t = str(int(time.time() * 1e9) - (7 * 24 * 60 * 60 * 10**9))
        fresh_data = fu.read(
            conf.DB_FILE,
            conf.TRADES_FRAME,
            where="index > " + t
        )
        if not fresh_data.empty:
            fresh_data = resamp.resampleTradeData(fresh_data)

            trainer.prepareAlphas(fresh_data)
            timestamp = fresh_data.index[-1]
            current_price = fresh_data.at[timestamp, "close"]
            strat.analyse(
                feature_index=-1,  # there should be only one feature
                current_price=current_price,
                timestamp=timestamp
            )

        if not _delay():
            return


def fetch(args):
    """Fetch raw trade data since the beginning of times"""

    _initCmd(args.graph)

    for f in [conf.DB_FILE]:
        if os.path.isfile(f):
            os.remove(f)  # TODO: warn user / create backup?

    raw_data = api.dumpData("0")
    while len(raw_data.index) == 1000:  # TODO: this is too much kraken specific
        log.debug(
            "Fetched data from " + str(raw_data.index[0])
            + " to " + str(raw_data.index[-1])
        )
        if not _delay():
            return

        raw_data = api.dumpData()


def backtest(args):
    """
    Just a naive backtester

    It will call the trained strategies on each test data point
    """

    _initCmd(args.graph, simulate=True, with_api=False)

    big_fat_data = _getData()[1]
    trainer.prepareAlphas(big_fat_data)
    big_fat_data_index = big_fat_data.index.values
    big_fat_data_prices = big_fat_data["close"].values
    del big_fat_data

    start_time = time.time()

    # pylint: disable=consider-using-enumerate
    for i in range(len(big_fat_data_index)):
        strat.analyse(
            feature_index=i,
            current_price=big_fat_data_prices[i],
            timestamp=big_fat_data_index[i]
        )
        if EXIT:
            return

    current_price = big_fat_data_prices[-1]
    score = ledger.BALANCE["crypto"] * current_price + ledger.BALANCE["quote"]
    hodl = current_price / big_fat_data_prices[0] * 100
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

    # _initCmd(args.graph, simulate=True, with_api=False)

    train_data, test_data = _getData()

    splits_size = int(len(train_data) / DATA_SET_LEN)
    splits = np.array_split(train_data, splits_size)

    start = splits_size - NUMBER_OF_TRAIN_SETS
    if start < 0:
        start = 0
    for i in range(start, splits_size):
        log.debug("Using train set", i + 1, "/", splits_size)

        trainer.prepareAlphas(splits[i], targets=True)
        trainer.trainAlphas()

        if args.graph:
            trainer.plotAlphas(splits[i])

    if args.graph:
        trainer.prepareAlphas(test_data, targets=False)
        trainer.plotAlphas(test_data)

        import matplotlib.pyplot as plt
        plt.show()
