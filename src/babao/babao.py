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

# from IPython import embed; embed()
# from ipdb import set_trace; set_trace()
# import babao; args = babao.babao._init(["-vv", "d"]); args.func(args)

from multiprocessing import Process, Lock

from prwlock import RWLock

import babao.arg as arg
import babao.config as conf
import babao.inputs.ledger.ledgerManager as lm
import babao.utils.date as du
import babao.utils.file as fu
import babao.utils.lock as lock
import babao.utils.log as log
import babao.utils.signal as sig
from babao.models.rootModel import RootModel


def _launchGraph():
    """Start the graph process"""

    # we import here, so matplotlib can stay an optional dependency
    import babao.graph as graph

    p = Process(
        target=graph.initGraph,
        args=(log.LOCK, fu.LOCK),
        name="babao-graph",
        daemon=True  # so we don't have to terminate it
    )
    p.start()


def _kthxbye():
    """KTHXBYE"""

    fu.closeStore()
    lock.tryUnlock(conf.LOCK_FILE)


def _init(args=None):
    """Initialize config and parse argv"""

    args = arg.parseArgv(args)
    log.initLogLevel(args.verbose, args.quiet)
    conf.readConfigFile(args.func.__name__)
    if not lock.tryLock(conf.LOCK_FILE) and not args.fuckit:
        log.error("Lock found (" + conf.LOCK_FILE + "), abort.")

    if args.func.__name__ in ["train", "backtest"]:
        du.setTime(du.EPOCH)
    else:
        log.setLock(Lock())
    if args.graph:
        fu.setLock(RWLock())
    fu.initStore(conf.DB_FILE)

    lm.initLedgers(
        simulate=args.func.__name__ != "wetRun",
        log_to_file=args.func.__name__ not in ["train", "backtest"]
    )
    RootModel()

    if args.graph and args.func.__name__ != "train":
        _launchGraph()
    sig.catchSignal()

    return args


def main(args=None):
    """Babao entry point"""

    args = _init(args)
    args.func(args)
    _kthxbye()
