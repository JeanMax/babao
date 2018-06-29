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
# import babao; args = babao.babao._init(["-vvgf", "t"]); args.func(args)

import babao.utils.log as log
import babao.utils.file as fu
import babao.utils.lock as lock
import babao.config as conf
import babao.parser as pars


def _kthxbye():
    """KTHXBYE"""

    fu.closeStore()
    lock.tryUnlock(conf.LOCK_FILE)


def _init(args=None):
    """Initialize config and parse argv"""

    args = pars.parseArgv(args)
    log.initLogLevel(args.verbose, args.quiet)
    conf.readConfigFile(args.func.__name__)

    if not lock.tryLock(conf.LOCK_FILE) and not args.fuckit:
        log.error("Lock file found (" + conf.LOCK_FILE + "), abort.")
    fu.initStore(conf.DB_FILE)

    return args


def main(args=None):
    """Babao entry point"""

    args = _init(args)
    args.func(args)
    _kthxbye()
