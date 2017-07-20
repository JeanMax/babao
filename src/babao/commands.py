"""Commands launched by conf.parseArgv"""

import time
import sys

import babao.api as api
import babao.resample as resamp
import babao.indicators as indic
import babao.strategy as strat


def mainLoop():
    """The stuffs that we'll want to repeat for our bot to work"""

    strat.analyse(
        indic.updateIndicators(
            resamp.resampleData(
                api.dumpData()  # TODO: this could use a renaming
            )
        )
    )


def dryRun(unused_args):
    """Real-time bot simulation"""

    api.initKey()

    while True:
        mainLoop()
        time.sleep(3)
        # TODO: sleep(API_DELAY - time(mainLoop()) + LIL_DELAY_JUST_IN_CASE)
        # time.sleep() shouldn't be used under 0.01s


def notImplemented(args):
    """Dummy"""

    print(repr(args))
    print("Sorry, this is not implemented yet :/")
    sys.exit()
