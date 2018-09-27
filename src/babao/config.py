"""Here we'll handle the config file and the various file/dir paths"""

import configparser as cp
import os

from babao.utils.enum import QuoteEnum, CryptoEnum

# globad vars
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".babao.d")
CONFIG_FILE = os.path.join(CONFIG_DIR, "babao.conf")
API_KEY_FILE = os.path.join(CONFIG_DIR, "kraken.key")  # TODO: move
LOCK_FILE = os.path.join(CONFIG_DIR, "babao.lock")  # TODO: move?
LOG_DIR = os.path.join(CONFIG_DIR, "log")
DATA_DIR = os.path.join(CONFIG_DIR, "data")
DB_FILE = os.path.join(DATA_DIR, "babao-database.hdf")  # TODO: move

# config vars
QUOTE = None
CRYPTOS = None  # TODO: infere from models
TIME_INTERVAL = None
MAX_GRAPH_POINTS = None

CURRENT_COMMAND = None


def readConfigFile(cmd_name="dry-run"):
    """Read config file and initialize file/dir paths"""

    # TODO: find a better way to handle config
    global QUOTE
    global CRYPTOS
    global TIME_INTERVAL
    global MAX_GRAPH_POINTS
    global CURRENT_COMMAND

    CURRENT_COMMAND = cmd_name
    config = cp.RawConfigParser()
    config.read(CONFIG_FILE)

    QUOTE = config.get(
        "babao",
        "QUOTE",
        fallback="EUR"
    )
    QUOTE = QuoteEnum[QUOTE]

    CRYPTOS = config.get(
        "babao",
        "CRYPTOS",
        fallback="ETH LTC XBT"
    )
    CRYPTOS = [CryptoEnum[c] for c in CRYPTOS.split()]

    TIME_INTERVAL = config.getint(
        "babao",
        "TIME_INTERVAL",
        fallback=5
    )

    MAX_GRAPH_POINTS = config.getint(
        "babao",
        "MAX_GRAPH_POINTS",
        fallback=420
    )

    # TODO: check if these vars are valid
