"""
This file will handle all the api requests

It will become an interface to the mutliples markets apis.
"""

import os
import pandas as pd

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
    and append it to ´conf.DB_FILE´

    If the argument ´since´ is empty, fetch the last data and store
    the ´LAST_DUMP´ timestamp into a file for next calls;
    Otherwise, fetch data since the given (stringified) timestamp
    """

    global LAST_DUMP
    if since is not None:
        LAST_DUMP = since
    elif not LAST_DUMP:
        if os.path.isfile(conf.DB_FILE):
            LAST_DUMP = str(
                fu.getLastRows(conf.DB_FILE, conf.TRADES_FRAME, 1).index[0]
            )

    raw_data, LAST_DUMP = kraken.getRawTrades(LAST_DUMP)
    if not raw_data.empty:
        last_row = pd.DataFrame(
            [raw_data.iloc[-1].values],
            index=[int(LAST_DUMP)],
            columns=conf.RAW_TRADES_COLUMNS
        )
        raw_data = raw_data.iloc[:-1].append(last_row)
        fu.write(conf.DB_FILE, conf.TRADES_FRAME, raw_data)

    return raw_data
