"""Here we'll handle the config file and the various file/dir paths"""

import os
import time
import configparser as cp

# globad vars
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".babao.d")
CONFIG_FILE = os.path.join(CONFIG_DIR, "babao.conf")
API_KEY_FILE = os.path.join(CONFIG_DIR, "kraken.key")
LOCAL_LOCK_FILE = os.path.join(CONFIG_DIR, "babao-local.lock")
GLOBAL_LOCK_FILE = os.path.join(CONFIG_DIR, "babao-global.lock")

LAST_DUMP_FILE = None
RAW_TRADES_FILE = None
UNSAMPLED_TRADES_FILE = None
RESAMPLED_TRADES_FILE = None
INDICATORS_FILE = None
RAW_LEDGER_FILE = None

RAW_TRADES_COLUMNS = [
    "price", "volume", "buy-sell", "market-limit", "vwap"
]
RESAMPLED_TRADES_COLUMNS = [
    "open", "high", "low", "close",
    "vwap", "volume", "count"
]
INDICATORS_COLUMNS = [
    "SMA_vwap_1", "SMA_volume_1",
    "SMA_vwap_2", "SMA_volume_2",
    "SMA_vwap_3", "SMA_volume_3"
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
    global LAST_DUMP_FILE
    global RAW_TRADES_FILE
    global UNSAMPLED_TRADES_FILE
    global RESAMPLED_TRADES_FILE
    global INDICATORS_FILE
    global RAW_LEDGER_FILE

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
    post = str(TIME_INTERVAL) + "Min.csv"

    LAST_DUMP_FILE = pre + "-lastDump.timestamp"

    INDICATORS_FILE = pre + "-indicators-" + post

    RAW_TRADES_FILE = pre + "-raw-trades.csv"
    UNSAMPLED_TRADES_FILE = pre + "-unsampled-trades-" + post
    RESAMPLED_TRADES_FILE = pre + "-resampled-trades-" + post

    if cmd_name == "backtest":
        cmd_name += time.strftime("-%y-%m-%d_%H-%M-%S.csv")
    RAW_LEDGER_FILE = pre + "-raw-ledger-" + cmd_name + ".csv"
