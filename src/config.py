"""TODO"""

import os
import configparser as cp

# globad vars
ROOT_DIR = os.path.realpath(
    os.path.join(os.path.dirname(__file__), "..")
)
CONFIG_DIR = os.path.join(ROOT_DIR, "config")
CONFIG_FILE = os.path.join(CONFIG_DIR, "babao.conf")
API_KEY_FILE = os.path.join(CONFIG_DIR, "kraken.key")

# config vars (TODO: this kinda ugly)
LOG_DIR = None
DATA_DIR = None
SLEEP_DELAY = None
TIME_INTERVAL = None
ASSET_PAIR = None


def readConf():
    # TODO: find a better way to handle config
    global SLEEP_DELAY
    global TIME_INTERVAL
    global ASSET_PAIR
    global LOG_DIR
    global DATA_DIR

    conf = cp.RawConfigParser()
    conf.read(CONFIG_FILE)

    SLEEP_DELAY = int(conf.get("babao", "SLEEP_DELAY", fallback=10))
    TIME_INTERVAL = int(conf.get("babao", "TIME_INTERVAL", fallback=1))
    ASSET_PAIR = str(conf.get("babao", "ASSET_PAIR", fallback="XXBTZEUR"))
    LOG_DIR = str(conf.get("babao", "LOG_DIR", fallback="/tmp"))
    DATA_DIR = str(conf.get("babao", "DATA_DIR", fallback=os.path.join(ROOT_DIR, "data")))
