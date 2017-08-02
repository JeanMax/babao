"""Commands launched by parseArgv"""

import time
import sys
import os
import signal

import babao.config as conf
import babao.utils.log as log
import babao.api.api as api
import babao.data.resample as resamp
import babao.data.indicators as indic
import babao.strategy.strategy as strat
import babao.strategy.ledger as ledger

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


def initCmd(graph=False, simulate=False):
    """
    Generic command init function

    Init: lock file, signal handlers, api key, graph
    """

    # init lock file
    open(conf.LOCK_FILE, "w")

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

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
        strat.analyse()
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


def notImplemented(args):
    """Dummy"""

    print(repr(args))
    print("Sorry, this is not implemented yet :/")
    sys.exit(42)
