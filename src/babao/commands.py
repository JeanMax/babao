"""Commands launched by parseArgv"""

import time
import os
import signal

import babao.utils.log as log
import babao.utils.fileutils as fu
import babao.utils.lock as lock
import babao.config as conf
import babao.api.api as api
import babao.data.resample as resamp
import babao.data.indicators as indic
import babao.data.ledger as ledger
import babao.strategy.strategy as strat
import babao.strategy.trainer as trainer

EXIT = 0
TICK = None


def _signalHandler(signal_code, unused_frame):
    """Catch signal INT/TERM, so we won't exit while playing with data files"""

    global EXIT
    EXIT = 128 + signal_code


def _delay():
    """
    Sleep the min amount of time required to still be friend with the api

    Also handle a lock file to avoid having the graph read data while we write
    Return False if a signal have been caught (you need to exit).
    """

    if EXIT:
        return False

    lock.tryUnlock(conf.LOCAL_LOCK_FILE)

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

    lock.tryLock(conf.LOCAL_LOCK_FILE)
    time.sleep(0.1)  # TODO: define LIL_DELAY_JUST_IN_CASE

    return not bool(EXIT)


def _launchGraph():
    """Start the graph process"""

    # we import here, so matplotlib can stay an optional dependency
    from multiprocessing import Process
    import babao.graph as graph

    p = Process(
        target=graph.initGraph,
        # args=(full_data,),
        # name="babao-graph",
        daemon=True  # so we don't have to terminate it
    )
    p.start()


def _initCmd(graph=False, simulate=False, with_api=True):
    """
    Generic command init function

    Init: lock file, signal handlers, api key, graph
    """

    lock.tryLock(conf.LOCAL_LOCK_FILE)

    signal.signal(signal.SIGINT, _signalHandler)
    signal.signal(signal.SIGTERM, _signalHandler)

    strat.initLastTransactionPrice()
    trainer.loadAlphas()

    if with_api:
        api.initKey()

    ledger.initBalance()
    if simulate and not os.path.isfile(conf.RAW_LEDGER_FILE):
        ledger.logQuoteDeposit(100)

    if graph:
        _launchGraph()


def _getData():
    """Return the whole dataset splitted in two parts: (train, test)"""

    full_data = fu.readFile(
        conf.RESAMPLED_TRADES_FILE,
        conf.RESAMPLED_TRADES_COLUMNS,
    ).join(
        fu.readFile(
            conf.INDICATORS_FILE,
            conf.INDICATORS_COLUMNS,
        )
    )
    # TODO: we remove the head because there is not enough volume at first
    full_data = full_data.tail(int(len(full_data) * 0.6))
    split_index = int(len(full_data) * 0.7)

    return full_data[:split_index], full_data[split_index:]


def wetRun(args):
    """Dummy"""
    print(repr(args))
    print("Sorry, this is not implemented yet :/")


def dryRun(args):
    """Real-time bot simulation"""

    _initCmd(args.graph, simulate=True)

    while True:
        indic.updateIndicators(
            resamp.resampleTradeData(
                api.dumpData()  # TODO: this could use a renaming
            )
        )

        fresh_data = fu.getLastLines(
            conf.RESAMPLED_TRADES_FILE,
            1,
            conf.RESAMPLED_TRADES_COLUMNS
        ).join(
            fu.getLastLines(
                conf.INDICATORS_FILE,
                1,
                conf.INDICATORS_COLUMNS
            )
        )

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

    for f in [conf.LAST_DUMP_FILE,
              conf.RAW_TRADES_FILE,
              conf.UNSAMPLED_TRADES_FILE,
              conf.RESAMPLED_TRADES_FILE,
              conf.INDICATORS_FILE]:
        if os.path.isfile(f):
            os.remove(f)  # TODO: warn user / create backup?

    raw_data = api.dumpData("0")
    indic.updateIndicators(
        resamp.resampleTradeData(raw_data)
    )
    while len(raw_data.index) == 1000:  # TODO: this is too much kraken specific
        log.debug(
            "Fetched data from " + str(raw_data.index[0])
            + " to " + str(raw_data.index[-1])
        )
        if not _delay():
            return

        raw_data = api.dumpData()
        indic.updateIndicators(
            resamp.resampleTradeData(raw_data)
        )


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
        while _delay():
            pass


def train(args):
    """Train the various (awesome) algorithms"""

    # _initCmd(args.graph, simulate=True, with_api=False)

    train_data, test_data = _getData()
    trainer.prepareAlphas(train_data, targets=True)
    trainer.trainAlphas()

    if args.graph:
        trainer.plotAlphas(train_data)
        trainer.prepareAlphas(test_data, targets=False)
        trainer.plotAlphas(test_data)
        import matplotlib.pyplot as plt
        plt.show()
