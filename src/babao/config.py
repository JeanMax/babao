"""Here we'll handle the config file and the various file/dir paths"""

import os
import time
import configparser as cp

# globad vars
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".babao.d")
CONFIG_FILE = os.path.join(CONFIG_DIR, "babao.conf")
API_KEY_FILE = os.path.join(CONFIG_DIR, "kraken.key")
LOCK_FILE = os.path.join(CONFIG_DIR, "babao.lock")

DB_FILE = None
TRADES_FRAME = "trades"
LEDGER_FRAME = None
MODEL_EXTREMA_FILE = None
MODEL_TENDENCY_FILE = None

RAW_TRADES_COLUMNS = [
    "price", "volume"
]
RESAMPLED_TRADES_COLUMNS = [
    "open", "high", "low", "close",
    "vwap", "volume", "count"
]
RAW_LEDGER_COLUMNS = [
    "type", "price",
    "crypto_vol", "quote_vol",
    "crypto_fee", "quote_fee",
    "crypto_bal", "quote_bal"
]
RESAMPLED_LEDGER_COLUMNS = [
    "crypto_bal", "quote_bal"
]

# config vars
LOG_DIR = None
DATA_DIR = None
ASSET_PAIR = None
TIME_INTERVAL = None
MAX_GRAPH_POINTS = None


def readConfigFile(cmd_name="unamed"):
    """Read config file and initialize file/dir paths"""

    # TODO: find a better way to handle config
    global LOG_DIR
    global DATA_DIR
    global ASSET_PAIR
    global TIME_INTERVAL
    global MAX_GRAPH_POINTS
    global DB_FILE
    global LEDGER_FRAME
    global MODEL_EXTREMA_FILE
    global MODEL_TENDENCY_FILE

    config = cp.RawConfigParser()
    config.read(CONFIG_FILE)

    LOG_DIR = config.get(
        "babao",
        "LOG_DIR",
        fallback="/tmp"
    )
    DATA_DIR = config.get(
        "babao",
        "DATA_DIR",
        fallback=os.path.join(CONFIG_DIR, "data")
    )
    ASSET_PAIR = config.get(
        "babao",
        "ASSET_PAIR",
        fallback="XXBTZEUR"
    )
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

    pre = os.path.join(DATA_DIR, ASSET_PAIR)

    DB_FILE = os.path.join(DATA_DIR, ASSET_PAIR) + "-database.hdf"
    LEDGER_FRAME = "ledger_" + cmd_name
    if cmd_name == "backtest":
        LEDGER_FRAME += time.strftime("_%y%m%d_%H%M%S")  # TODO: remove this

    MODEL_EXTREMA_FILE = pre + "-extrema.pkl"
    MODEL_TENDENCY_FILE = pre + "-tendency.h5"
