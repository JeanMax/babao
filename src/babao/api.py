"""This file will handle all the api requests"""

import os
import time
import http
import socket
import krakenex
import pandas as pd

import babao.config as conf
import babao.log as log
import babao.fileutils as fu

K = krakenex.API()
C = krakenex.Connection()
LAST_DUMP = ""

# TODO: block sig INT/TERM


def initKey():
    """Load the api key from config folder"""

    K.load_key(conf.API_KEY_FILE)


def kraken_doRequest(method, req=None):
    """General function for kraken api requests"""

    global C
    if not req:
        req = {}

    # we loop in case of request error (503...)
    fail_counter = 1
    while fail_counter > 0:  # really nice loop bro, respect... no goto tho
        try:
            if method == "Trades":
                res = K.query_public(method, req, C)
            else:
                res = K.query_private(method, req, C)
        except (socket.timeout, socket.error, http.client.BadStatusLine) as e:
            log.error("Network error while querying Kraken API!\n" + repr(e))
        except http.client.CannotSendRequest as e:
            log.error(
                "http.client error while querying Kraken API!"
                + "Restarting connection..."
                + repr(e)
            )
            C.close()
            C = krakenex.Connection()
        except ValueError as e:
            log.error("ValueError while querying Kraken API!\n" + repr(e))
        # except Exception as e:
            # log.error("Exception while querying Kraken API!\n" + repr(e))
        else:
            err = res.get("error", [])
            if err:
                for e in err:
                    log.error("Exception returned by Kraken API!\n" + e)
            else:
                return res["result"]
        log.debug("Connection fail #" + str(fail_counter))
        fail_counter += 1
        time.sleep(0.5)


def kraken_getBalance():
    """Return account balance (associatives arrays, keys = assets)"""

    res = kraken_doRequest("Balance")
    return res


def kraken_getRawTrades():
    """
    Fetch last trades from api and return them as a DataFrame

    (only fetch results since ´LAST_DUMP´)
    index -> time,
    columns=["price", "volume", "buy-sell", "market-limit", "vwap"]
    """

    global LAST_DUMP
    if not LAST_DUMP:
        if os.path.isfile(conf.LAST_DUMP_FILE):
            with open(conf.LAST_DUMP_FILE, "r") as f:
                LAST_DUMP = f.readline()

    res = kraken_doRequest("Trades", {
        "pair": conf.ASSET_PAIR,
        "since": LAST_DUMP
    })

    LAST_DUMP = res["last"]
    with open(conf.LAST_DUMP_FILE, "w") as f:
        f.write(LAST_DUMP)

    df = pd.DataFrame(
        res[conf.ASSET_PAIR],
        columns=["price", "volume", "time", "buy-sell", "market-limit", "misc"],
        dtype=float  # TODO: dtypes: object(2) (replace bsml letters with 0/1?)
    )
    df.index = df["time"].astype(int)
    del df["misc"]
    # del df ["market-limit"]  # TODO: this could be useful
    # del df["buy-sell"]  # TODO: this could be useful
    del df["time"]

    # we'll need this later for resampling
    df["vwap"] = df["price"] * df["volume"]

    return df


def dumpData():
    """Return a DataFrame of the last trades and append it to ´conf.RAW_FILE´"""

    log.debug("Entering dumpData()")

    raw_data = kraken_getRawTrades()
    fu.writeFile(conf.RAW_FILE, raw_data, mode="a")

    return raw_data
