"""Here we'll handle the config file and the various file/dir paths"""

import configparser as cp
import os

from babao.utils.enum import QuoteEnum, CryptoEnum

# globad vars
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".babao.d")
CONFIG_FILE = os.path.join(CONFIG_DIR, "babao.conf")
API_KEY_FILE = os.path.join(CONFIG_DIR, "kraken.key")
LOCK_FILE = os.path.join(CONFIG_DIR, "babao.lock")
LOG_DIR = os.path.join(CONFIG_DIR, "log")
DATA_DIR = os.path.join(CONFIG_DIR, "data")
DB_FILE = os.path.join(DATA_DIR, "babao-database.hdf")

# TODO: don't
MODEL_MACD_FILE = os.path.join(DATA_DIR, "macd.pkl")
MODEL_EXTREMA_FILE = os.path.join(DATA_DIR, "extrema.pkl")
MODEL_TENDENCY_FILE = os.path.join(DATA_DIR, "tendency.h5")
MODEL_QLEARN_FILE = os.path.join(DATA_DIR, "qlearn.h5")

# config vars
QUOTE = None
CRYPTOS = None
TIME_INTERVAL = None
MAX_GRAPH_POINTS = None


def readConfigFile(unused_cmd_name="unamed"):
    """Read config file and initialize file/dir paths"""

    # TODO: find a better way to handle config
    global QUOTE
    global CRYPTOS
    global TIME_INTERVAL
    global MAX_GRAPH_POINTS

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
