"""Commands launched by conf.parseArgv"""

import time
import sys
import os
import signal
from multiprocessing import Process

import babao.config as conf
import babao.utils.log as log
import babao.utils.fileutils as fu
import babao.api.api as api
import babao.data.resample as resamp
import babao.data.indicators as indic
import babao.data.graph as graph
import babao.strategy.strategy as strat

EXIT = False
TICK = None


def signal_handler(unused_signal, unused_frame):
    """TODO"""

    global EXIT
    EXIT = True


def delay():
    """TODO"""

    global TICK
    if TICK is not None:
        delta = time.time() - TICK
    else:
        delta = 0
    log.debug("Loop took " + str(delta) + "s")

    delta = 3 - delta + 0.1  # TODO: define API_DELAY, LIL_DELAY_JUST_IN_CASE
    if delta > 0:
        time.sleep(delta)
    TICK = time.time()


def dryRun(args):
    """Real-time bot simulation"""

    api.initKey()
    if args.graph:
        full_data = fu.getLastLines(
            conf.RESAMPLED_FILE,
            graph.MAX_POINTS,
            conf.RESAMPLED_COLUMNS
        )
        full_data = full_data.join(
            fu.getLastLines(
                conf.INDICATORS_FILE,
                graph.MAX_POINTS,
                conf.INDICATORS_COLUMNS
            )
        )
        p = Process(target=graph.initGraph, args=(full_data,))
        p.start()

    signal.signal(signal.SIGINT, signal_handler)
    while True:
        full_data = indic.updateIndicators(
            resamp.resampleData(
                api.dumpData()  # TODO: this could use a renaming
            )
        )
        strat.analyse(full_data)
        if EXIT:
            break
        delay()

    if args.graph and p.is_alive():
        p.terminate()


def fetch(args):
    """fetch raw trade data since the beginning of times"""

    api.initKey()

    for f in [conf.LAST_DUMP_FILE,
              conf.RAW_FILE,
              conf.UNSAMPLED_FILE,
              conf.RESAMPLED_FILE,
              conf.INDICATORS_FILE]:
        if os.path.isfile(f):
            os.remove(f)  # TODO: warn user / create backup?

    signal.signal(signal.SIGINT, signal_handler)
    raw_data = api.dumpData("0")
    full_data = indic.updateIndicators(
        resamp.resampleData(raw_data)
    )
    if args.graph:
        p = Process(target=graph.initGraph, args=(full_data,))
        p.start()

    while len(raw_data.index) == 1000:  # TODO: this is too much kraken specific
        log.debug(
            "Fetched data from " + str(raw_data.index[0])
            + " to " + str(raw_data.index[-1])
        )
        if EXIT:
            break
        delay()

        # TODO: block sig INT/TERM
        raw_data = api.dumpData()
        full_data = indic.updateIndicators(
            resamp.resampleData(raw_data)
        )

    if args.graph and p.is_alive():
        p.terminate()


def notImplemented(args):
    """Dummy"""

    print(repr(args))
    print("Sorry, this is not implemented yet :/")
    sys.exit(42)
