"""TODO"""

import os
import configparser as cp

# globad vars
CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".babao.d")
CONFIG_FILE = os.path.join(CONFIG_DIR, "babao.conf")
API_KEY_FILE = os.path.join(CONFIG_DIR, "kraken.key")

# config vars (TODO: this is kinda ugly)
LOG_DIR = None
DATA_DIR = None
SLEEP_DELAY = None
TIME_INTERVAL = None
ASSET_PAIR = None


def readFile():
    # TODO: find a better way to handle config
    global SLEEP_DELAY
    global TIME_INTERVAL
    global ASSET_PAIR
    global LOG_DIR
    global DATA_DIR

    config = cp.RawConfigParser()
    config.read(CONFIG_FILE)

    SLEEP_DELAY = config.getint("babao", "SLEEP_DELAY", fallback=10)
    TIME_INTERVAL = config.getint("babao", "TIME_INTERVAL", fallback=1)
    ASSET_PAIR = config.get("babao", "ASSET_PAIR", fallback="XXBTZEUR")
    LOG_DIR = config.get("babao", "LOG_DIR", fallback="/tmp")
    DATA_DIR = config.get("babao", "DATA_DIR", fallback=os.path.join(CONFIG_DIR, "data"))
