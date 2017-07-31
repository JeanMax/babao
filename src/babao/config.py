"""Here we'll handle the config file and the various file/dir paths"""

import os
import time
import configparser as cp

# globad vars
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".babao.d")
CONFIG_FILE = os.path.join(CONFIG_DIR, "babao.conf")
API_KEY_FILE = os.path.join(CONFIG_DIR, "kraken.key")
LOCK_FILE = os.path.join(CONFIG_DIR, "babao.lock")

LAST_DUMP_FILE = None
RAW_FILE = None
UNSAMPLED_FILE = None
RESAMPLED_FILE = None
INDICATORS_FILE = None
LEDGER_FILE = None

RAW_COLUMNS = ["price", "volume", "buy-sell", "market-limit", "vwap"]
RESAMPLED_COLUMNS = ["open", "high", "low", "close", "vwap", "volume", "count"]
INDICATORS_COLUMNS = [
    "SMA_vwap_1", "SMA_volume_1",
    "SMA_vwap_2", "SMA_volume_2",
    "SMA_vwap_3", "SMA_volume_3"
]
LEDGER_COLUMNS = ["price", "volume", "buy-sell", "market-limit"]

# config vars
LOG_DIR = None
DATA_DIR = None
ASSET_PAIR = None
TIME_INTERVAL = None


def readConfigFile():
    """Read config file and initialize file/dir paths"""

    # TODO: find a better way to handle config
    global LOG_DIR
    global DATA_DIR
    global ASSET_PAIR
    global TIME_INTERVAL
    global LAST_DUMP_FILE
    global RAW_FILE
    global UNSAMPLED_FILE
    global RESAMPLED_FILE
    global INDICATORS_FILE
    global LEDGER_FILE

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
        fallback=1
    )

    LAST_DUMP_FILE = os.path.join(
        DATA_DIR,
        ASSET_PAIR + "-last_dump.timestamp"
    )
    RAW_FILE = os.path.join(
        DATA_DIR,
        ASSET_PAIR + "-raw.csv"
    )
    UNSAMPLED_FILE = os.path.join(
        DATA_DIR,
        ASSET_PAIR + "-unsampled-" + str(TIME_INTERVAL) + "Min.csv"
    )
    RESAMPLED_FILE = os.path.join(
        DATA_DIR,
        ASSET_PAIR + "-resampled-" + str(TIME_INTERVAL) + "Min.csv"
    )
    INDICATORS_FILE = os.path.join(
        DATA_DIR,
        ASSET_PAIR + "-indicators-" + str(TIME_INTERVAL) + "Min.csv"
    )
    LEDGER_FILE = os.path.join(
        DATA_DIR,
        ASSET_PAIR + time.strftime("-ledger-simulation-%y-%m-%d_%H-%M-%S.csv")
        # TODO: bot-mode only
    )
