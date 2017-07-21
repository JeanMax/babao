"""Some utils functions for logging"""

import time

VERBOSE = False


def initLogLevel(verbose):
    """Initialize log level based on verbose flag"""

    global VERBOSE
    if verbose:
        VERBOSE = True


def _log(header, msg):
    """Genreral logging function, shouldn't be used directly"""

    print(
        header
        + time.strftime("\033[37;01m [%Y/%m/%d %H:%M:%S]\033[0m\n")
        + msg
        + "\n"
    )


def error(msg):
    """Log an error (red)"""

    _log("\033[31;01m[ERROR]", msg)


def warning(msg):
    """Log a warning (yellow)"""

    if VERBOSE:
        _log("\033[33;01m[WARNING]", msg)


def debug(msg):
    """Log a debug (purple)"""

    if VERBOSE:
        _log("\033[35;01m[DEBUG]", msg)


def log(msg):
    """Log a simple message (blue)"""

    _log("\033[34;01m[LOG]", msg)
