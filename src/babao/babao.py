"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mbabao` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``babao.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``babao.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""

import time
import argparse

# from IPython import embed
# from ipdb import set_trace

import babao.config as conf
import babao.api as api
import babao.resample as resamp
import babao.indicators as indic
import babao.strategy as strat

# TODO: for some reasons this was outside any scope in the example
parser = argparse.ArgumentParser(description='Command description.')
parser.add_argument('names', metavar='NAME', nargs=argparse.ZERO_OR_MORE,
                    help="A name of something.")


def mainLoop():
    """TODO"""

    strat.analyse(
        indic.updateIndicators(
            resamp.resampleData(
                api.dumpData()  # TODO: this could use a renaming
            )
        )
    )


def init():
    """TODO"""

    conf.readFile()


def main(args=None):
    """TODO"""

    try:
        args = parser.parse_args(args=args)
    except:
        parser.print_help()
        exit

    init()
    while True:
        mainLoop()
        time.sleep(3)
        # TODO: sleep(API_DELAY - time(mainLoop()) + LIL_DELAY_JUST_IN_CASE)
        # time.sleep() shouldn't be used under 0.01s
