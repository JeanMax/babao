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
        + time.strftime(WHITE + " [%Y/%m/%d %H:%M:%S]\n" + RESET)
        + msg
        + "\n",
        file=file
    )


def error(msg):
    """Log an error (red)"""

    _log(RED + "[ERROR]", msg, file=sys.stderr)
    sys.exit(42)


def log(msg):
    """Log a simple message (blue)"""

    if VERBOSE >= 1:
        _log(BLUE + "[LOG]", msg)


def warning(msg):
    """Log a warning (yellow)"""

    if VERBOSE >= 2:
        _log(YELLOW + "[WARNING]", msg, file=sys.stderr)


def debug(msg):
    """Log a debug (magenta)"""

    if VERBOSE >= 3:
        _log(MAGENTA + "[DEBUG]", msg)
