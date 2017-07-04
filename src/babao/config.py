"""TODO"""

import os
import configparser as cp

# globad vars
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".babao.d")
CONFIG_FILE = os.path.join(CONFIG_DIR, "babao.conf")
API_KEY_FILE = os.path.join(CONFIG_DIR, "kraken.key")

LAST_DUMP_FILE = None
RAW_FILE = None
UNSAMPLED_FILE = None  #TODO: rename, it's actually resampled
RESAMPLED_FILE = None
INDICATORS_FILE = None

# config vars (TODO: this is kinda ugly)
LOG_DIR = None
DATA_DIR = None
ASSET_PAIR = None
TIME_INTERVAL = None


def readFile():
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

    config = cp.RawConfigParser()
    config.read(CONFIG_FILE)

    LOG_DIR = config.get("babao", "LOG_DIR", fallback="/tmp")
    DATA_DIR = config.get("babao", "DATA_DIR", fallback=os.path.join(CONFIG_DIR, "data"))
    ASSET_PAIR = config.get("babao", "ASSET_PAIR", fallback="XXBTZEUR")
    TIME_INTERVAL = config.getint("babao", "TIME_INTERVAL", fallback=1)

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
