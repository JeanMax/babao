"""Here we'll handle the config file and the various file/dir paths"""

import os
import configparser as cp

# globad vars
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".babao.d")
CONFIG_FILE = os.path.join(CONFIG_DIR, "babao.conf")
API_KEY_FILE = os.path.join(CONFIG_DIR, "kraken.key")
LOCK_FILE = os.path.join(CONFIG_DIR, "babao.lock")

MODEL_MACD_FILE = None
MODEL_EXTREMA_FILE = None
MODEL_TENDENCY_FILE = None
MODEL_QLEARN_FILE = None

# config vars
LOG_DIR = None  # useless and annoying... just let the user symlink if needed
DATA_DIR = None  # idem
ASSET_PAIR = None  # TODO: QUOTE, CRYPTOS
TIME_INTERVAL = None
MAX_GRAPH_POINTS = None
DB_FILE = None


def readConfigFile(unused_cmd_name="unamed"):
    """Read config file and initialize file/dir paths"""

    # TODO: find a better way to handle config
    global LOG_DIR
    global DATA_DIR
    global ASSET_PAIR
    global TIME_INTERVAL
    global MAX_GRAPH_POINTS
    global DB_FILE
    global MODEL_MACD_FILE
    global MODEL_EXTREMA_FILE
    global MODEL_TENDENCY_FILE
    global MODEL_QLEARN_FILE

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
    DB_FILE = os.path.join(DATA_DIR, "babao-database.hdf")

    MODEL_MACD_FILE = pre + "-macd.pkl"
    MODEL_EXTREMA_FILE = pre + "-extrema.pkl"
    MODEL_TENDENCY_FILE = pre + "-tendency.h5"
    MODEL_QLEARN_FILE = pre + "-qlearn.h5"
