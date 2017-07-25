"""Some utils functions for logging"""

import sys
import time

VERBOSE = 1


def initLogLevel(verbose, quiet):
    """Initialize log level based on verbose flag"""

    global VERBOSE
    if quiet:
        VERBOSE = 0
    elif verbose:
        VERBOSE = verbose


def _log(header, msg, file=sys.stdout):
    """Genreral logging function, shouldn't be used directly"""

    print(
        header
        + time.strftime("\033[37;01m [%Y/%m/%d %H:%M:%S]\033[0m\n")
        + msg
        + "\n",
        file=file
    )


def error(msg):
    """Log an error (red)"""

    _log("\033[31;01m[ERROR]", msg, file=sys.stderr)
    sys.exit(42)


def log(msg):
    """Log a simple message (blue)"""

    if VERBOSE >= 1:
        _log("\033[34;01m[LOG]", msg)


def warning(msg):
    """Log a warning (yellow)"""

    if VERBOSE >= 2:
        _log("\033[33;01m[WARNING]", msg, file=sys.stderr)


def debug(msg):
    """Log a debug (purple)"""

    if VERBOSE >= 3:
        _log("\033[35;01m[DEBUG]", msg)
