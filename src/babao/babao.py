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

# from IPython import embed
# from ipdb import set_trace

import argparse

import babao.log as log
import babao.config as conf
import babao.commands as cmd


def parseArgv(args):
    """Parse argv ARGS"""

    parser = argparse.ArgumentParser(
        description="A bitcoin trading machine.",
        epilog="Run 'babao <command> --help' for detailed help."
    )
    parser.add_argument(
        "-v", "--verbose",
        help="increase output verbosity",
        action="store_true"
    )
    parser.add_argument(
        "-g", "--graph",
        help="show a chart (matplotlib)",
        action="store_true"
    )

    # group = parser.add_mutually_exclusive_group()
    subparsers = parser.add_subparsers(
        title="commands",
        metavar="<command> [<args>]"
    )

    parser_d = subparsers.add_parser(
        "dry-run",
        aliases="d",
        help="real-time bot simulation",
        description="real-time bot simulation",  # TODO
    )
    parser_d.set_defaults(func=cmd.dryRun)

    parser_w = subparsers.add_parser(
        "wet-run",
        aliases="w",
        help="real-time bot with real-money!",
        description="real-time bot with real-money!",  # TODO
    )
    parser_w.set_defaults(func=cmd.notImplemented)

    parser_t = subparsers.add_parser(
        "training",
        aliases="t",
        help="train bot on the given raw trade data file",
        description="train bot on the given raw trade data file",  # TODO
    )
    parser_t.add_argument('FILE', help="raw trade data file")
    parser_t.set_defaults(func=cmd.notImplemented)

    parser_b = subparsers.add_parser(
        "backtest",
        aliases="b",
        help="test strategy on the given raw trade data file",
        description="test strategy on the given raw trade data file",  # TODO
    )
    parser_b.add_argument('FILE', help="raw trade data file")
    parser_b.set_defaults(func=cmd.notImplemented)

    parser_f = subparsers.add_parser(
        "fetch",
        aliases="f",
        help="fetch raw trade data since the given date",
        description="fetch raw trade data since the given date",  # TODO
    )
    parser_f.add_argument('TIMESTAMP', type=int, default=0, help="start date")
    parser_f.set_defaults(func=cmd.notImplemented)

    args = parser.parse_args(args=args)

    try:
        args.func
    except AttributeError:
        parser.print_help()
        parser.exit()

    return args


def init(args=None):
    """Initialize config and parse argv"""

    conf.readConfigFile()
    args = parseArgv(args)
    log.initLogLevel(args.verbose)
    return args


def main(args=None):
    """Babao entry point"""

    args = init()
    args.func(args)
