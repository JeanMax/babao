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

import babao.config as conf
import babao.api as api
import babao.resample as resamp
import babao.indicators as indic


# TODO: for some reasons this was outside any scope in the example
parser = argparse.ArgumentParser(description='Command description.')
parser.add_argument('names', metavar='NAME', nargs=argparse.ZERO_OR_MORE,
                    help="A name of something.")

def mainLoop():
    time_interval = str(conf.TIME_INTERVAL) + "Min"

    resamp.resampleData(api.dumpData(), time_interval) #TODO: this could use a renaming
    indic.updateIndicators(time_interval)



def main(args=None):
    conf.readFile()
    args = parser.parse_args(args=args)
    print(args.names)           # DEBUG

    while True:
        mainLoop()
        time.sleep(3)
