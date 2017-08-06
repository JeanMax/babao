"""Commands launched by parseArgv"""

import time
import sys
import os
import signal

import babao.config as conf
import babao.utils.log as log
import babao.utils.fileutils as fu
import babao.api.api as api
import babao.data.resample as resamp
import babao.data.indicators as indic
import babao.strategy.strategy as strat
import babao.data.ledger as ledger

EXIT = 0
TICK = None


def signal_handler(signal_code, unused_frame):
    """Catch signal INT/TERM, so we won't exit while playing with data files"""

    global EXIT
    EXIT = 128 + signal_code


def delay():
    """
    Sleep the min amount of time required to still be friend with the api

    Also handle a lock file to avoid having the graph read data while we write;
    exit before sleeping if a signal have been caught.
    """

    if EXIT:
        sys.exit(EXIT)

    # TODO: should we block if the file exists at startup?
    if os.path.isfile(conf.LOCK_FILE):
        os.remove(conf.LOCK_FILE)

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

    open(conf.LOCK_FILE, "w")
    time.sleep(0.1)  # TODO: define LIL_DELAY_JUST_IN_CASE

    if EXIT:
        sys.exit(EXIT)


def launchGraph():
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


def initCmd(graph=False, simulate=False, with_api=True):
    """
    Generic command init function

    Init: lock file, signal handlers, api key, graph
    """

    # init lock file
    open(conf.LOCK_FILE, "w")

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    strat.initLastTransactionPrice()

    if with_api:
        api.initKey()

    ledger.initBalance()
    if simulate and not os.path.isfile(conf.RAW_LEDGER_FILE):
        ledger.logQuoteDeposit(100)

    if graph:
        launchGraph()


def dryRun(args):
    """Real-time bot simulation"""

    initCmd(args.graph, simulate=True)

    while True:
        indic.updateIndicators(
            resamp.resampleTradeData(
                api.dumpData()  # TODO: this could use a renaming
            )
        )
        strat.analyse(
            fu.getLastLines(
                conf.RESAMPLED_TRADES_FILE,
                strat.LOOK_BACK,
                conf.RESAMPLED_TRADES_COLUMNS
            ).join(
                fu.getLastLines(
                    conf.INDICATORS_FILE,
                    strat.LOOK_BACK,
                    conf.INDICATORS_COLUMNS
                )
            )
        )
        if args.graph:
            resamp.resampleLedgerData()
        delay()


def fetch(args):
    """fetch raw trade data since the beginning of times"""

    initCmd(args.graph)

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
        delay()

        raw_data = api.dumpData()
        indic.updateIndicators(
            resamp.resampleTradeData(raw_data)
        )


def backtest(args):
    """Just a naive backtester"""

    # with float < 64, smaller size but longer to process
    # (might be a cast issue somewhere else)
    big_fat_data = fu.readFile(
        conf.RESAMPLED_TRADES_FILE,
        conf.RESAMPLED_TRADES_COLUMNS,
        # dtype=dict([(x, "float32") for x in conf.RESAMPLED_TRADES_COLUMNS])
    ).join(
        fu.readFile(
            conf.INDICATORS_FILE,
            conf.INDICATORS_COLUMNS,
            # dtype=dict([(x, "float32") for x in conf.INDICATORS_COLUMNS])
        )
    )

    for col in big_fat_data.columns:
        if col not in strat.REQUIRED_COLUMNS:
            del big_fat_data[col]

    initCmd(args.graph, simulate=True, with_api=False)

    for i in range(len(big_fat_data) - strat.LOOK_BACK + 1):
        strat.analyse(
            big_fat_data.iloc[i: i + strat.LOOK_BACK]
        )

        if i % 50000 == 0:
            delay()
        #     if args.graph:
        #         delay()
        #         resamp.resampleLedgerData()
        if EXIT:
            sys.exit(EXIT)

    log.log(
        "Backtesting done! Score: "
        + str(round(float(
            ledger.BALANCE["quote"] + ledger.BALANCE["crypto"]
            * fu.getLastLines(
                conf.RESAMPLED_TRADES_FILE,
                1,
                conf.RESAMPLED_TRADES_COLUMNS
            ).iloc[0]["close"]
        )))
        + "% vs HODL: "
        + str(round(
            big_fat_data.at[big_fat_data.index[-1], "close"]
            / big_fat_data.at[big_fat_data.index[0], "close"]
            * 100
        ))
        + "%"
    )

    # if args.graph:
    #     resamp.resampleLedgerData()
    #     while not EXIT:
    #         delay()


def notImplemented(args):
    """Dummy"""

    print(repr(args))
    print("Sorry, this is not implemented yet :/")
    sys.exit(42)
