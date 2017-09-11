"""Commands launched by parseArgv"""

import time
import sys
import os
import signal

import babao.utils.log as log
import babao.utils.file as fu
import babao.utils.lock as lock
import babao.config as conf
import babao.api.api as api
import babao.data.resample as resamp
import babao.data.indicators as indic
import babao.strategy.strategy as strat
import babao.data.ledger as ledger

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

    if with_api:
        api.initKey()

    ledger.initBalance()
    if simulate and fu.getLastRows(conf.DB_FILE, conf.LEDGER_FRAME, 1).empty:
        ledger.logQuoteDeposit(100)

    if graph:
        _launchGraph()


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
            strat.analyse(
                fresh_data.values,
                timestamp=fresh_data.index[-1]
            )

        if not _delay():
            return


def fetch(args):
    """fetch raw trade data since the beginning of times"""

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
    """Just a naive backtester"""

    # with float < 64, smaller size but longer to process
    # (might be a cast issue somewhere else)
    big_fat_data = resamp.resampleTradeData(
        fu.read(conf.DB_FILE, conf.TRADES_FRAME)
    )

    big_fat_data["SMA_vwap_1"] = indic.SMA(big_fat_data["vwap"], 9)
    big_fat_data["SMA_vwap_2"] = indic.SMA(big_fat_data["vwap"], 26)

    for col in big_fat_data.columns:
        if col not in strat.REQUIRED_COLUMNS:
            del big_fat_data[col]
    big_fat_data_index = big_fat_data.index
    big_fat_data_values = big_fat_data.values

    _initCmd(args.graph, simulate=True, with_api=False)

    start_time = time.time()

    for i in range(len(big_fat_data_index) - strat.LOOK_BACK):
        strat.analyse(
            big_fat_data_values[i: i + strat.LOOK_BACK],
            timestamp=big_fat_data_index[i + strat.LOOK_BACK]
        )
        if EXIT:
            return

    log.log(
        "Backtesting done! Score: "
        + str(round(float(
            ledger.BALANCE["quote"] + ledger.BALANCE["crypto"]
            * big_fat_data.at[big_fat_data.index[-1], "close"]
        )))
        + "% vs HODL: "
        + str(round(
            big_fat_data.at[big_fat_data.index[-1], "close"]
            / big_fat_data.at[big_fat_data.index[0], "close"]
            * 100
        ))
        + "%"
    )
    log.debug(
        "Backtesting took "
        + str(round(time.time() - start_time, 3)) + "s"
    )

    if args.graph:
        while _delay():
            pass
        # TODO: exit if graph is closed


def notImplemented(args):
    """Dummy"""

    print(repr(args))
    print("Sorry, this is not implemented yet :/")
    sys.exit(42)
