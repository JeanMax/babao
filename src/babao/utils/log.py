"""Some utils functions for logging"""

import sys
import time

VERBOSE = 1

# BLACK = "\033[30;01m"
RED = "\033[31;01m"
# GREEN = "\033[32;01m"
YELLOW = "\033[33;01m"
BLUE = "\033[34;01m"
MAGENTA = "\033[35;01m"
# CYAN = "\033[36;01m"
WHITE = "\033[37;01m"
RESET = "\033[0m"

LOCK = None


def setLock(lock):
    """Store the given ´lock´ object for later use in logging"""
    global LOCK
    LOCK = lock


def initLogLevel(verbose, quiet):
    """Initialize log level based on verbose flag"""

    global VERBOSE
    if quiet:
        VERBOSE = 0
    elif verbose:
        VERBOSE = verbose


def _log(header, *args, **kwargs):
    """Genreral logging function, shouldn't be used directly"""

    if LOCK is not None:
        LOCK.acquire()
    print(
        *((WHITE + time.strftime("[%Y/%m/%d %H:%M:%S] ") + header + RESET, )
          + args),
        **kwargs
    )
    if LOCK is not None:
        LOCK.release()


def error(*args):
    """Log an error (red)"""

    _log(RED + "[ERROR]", *args, file=sys.stderr)
    sys.exit(42)


def info(*args):
    """Log a simple message (blue)"""

    if VERBOSE >= 1:
        _log(BLUE + "[INFO]", *args)


def warning(*args):
    """Log a warning (yellow)"""

    if VERBOSE >= 2:
        _log(YELLOW + "[WARNING]", *args, file=sys.stderr)


def debug(*args):
    """Log a debug (magenta)"""

    if VERBOSE >= 3:
        _log(MAGENTA + "[DEBUG]", *args)
