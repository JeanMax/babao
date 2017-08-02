"""
This file will handle all the api requests

It will become an interface to the mutliples markets apis.
"""

import os

import babao.config as conf
import babao.utils.fileutils as fu
import babao.api.kraken as kraken

LAST_DUMP = ""  # TODO: this is too much kraken specific


def initKey():
    """Call the (right) api init key"""

    kraken.initKey()


# TODO: move to /data module?
def dumpData(since=None):
    """
    Return a DataFrame of the last trades,
    and append it to ´conf.RAW_TRADES_FILE´

    If the argument ´since´ is empty, fetch the last data and store
    the ´LAST_DUMP´ timestamp into a file for next calls;
    Otherwise, fetch data since the given (stringified) timestamp
    """

    global LAST_DUMP
    if since is not None:
        LAST_DUMP = since
    elif not LAST_DUMP:
        if os.path.isfile(conf.LAST_DUMP_FILE):
            with open(conf.LAST_DUMP_FILE, "r") as f:
                LAST_DUMP = f.readline()

    raw_data, LAST_DUMP = kraken.getRawTrades(LAST_DUMP)

    fu.writeFile(conf.RAW_TRADES_FILE, raw_data, mode="a")
    with open(conf.LAST_DUMP_FILE, "w") as f:
        f.write(LAST_DUMP)

    return raw_data
