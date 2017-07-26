"""Commands launched by conf.parseArgv"""

import time
import sys
import os

import babao.config as conf
import babao.utils.log as log
import babao.api.api as api
import babao.data.resample as resamp
import babao.data.indicators as indic
import babao.strategy.strategy as strat


def dryRun(unused_args):
    """Real-time bot simulation"""

    api.initKey()

    while True:
        # TODO: block sig INT/TERM
        strat.analyse(
            indic.updateIndicators(
                resamp.resampleData(
                    api.dumpData()  # TODO: this could use a renaming
                )
            )
        )

        # TODO: sleep(API_DELAY - time(mainLoop()) + LIL_DELAY_JUST_IN_CASE)
        time.sleep(3)


def fetch(unused_args):
    """fetch raw trade data since the beginning of times"""

    api.initKey()

    for f in [conf.LAST_DUMP_FILE,
              conf.RAW_FILE,
              conf.UNSAMPLED_FILE,
              conf.RESAMPLED_FILE,
              conf.INDICATORS_FILE]:
        if os.path.isfile(f):
            os.remove(f)  # TODO: warn user / create backup?

    # TODO: block sig INT/TERM
    raw_data = api.dumpData("0")
    indic.updateIndicators(
        resamp.resampleData(raw_data)
    )
    while len(raw_data.index) == 1000:  # TODO: this is too much kraken specific
        log.debug("Fetched data since " + str(raw_data.index[0]))

        # TODO: sleep(API_DELAY - time(mainLoop()) + LIL_DELAY_JUST_IN_CASE)
        time.sleep(3)

        # TODO: block sig INT/TERM
        raw_data = api.dumpData()
        indic.updateIndicators(
            resamp.resampleData(raw_data)
        )


def notImplemented(args):
    """Dummy"""

    print(repr(args))
    print("Sorry, this is not implemented yet :/")
    sys.exit(42)
