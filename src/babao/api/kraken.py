"""Kraken market api methods"""

import os
import time
import http
import socket
import krakenex
import pandas as pd

import babao.config as conf
import babao.utils.log as log

K = krakenex.API()
C = krakenex.Connection()
LAST_DUMP = ""


def initKey():
    """Load the api key from config folder"""

    K.load_key(conf.API_KEY_FILE)


def doRequest(method, req=None):
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


def getBalance():
    """Return account balance (associatives arrays, keys = assets)"""

    res = doRequest("Balance")
    return res


def getRawTrades(last_dump=None):
    """
    Fetch last trades from api and return them as a DataFrame

    If the argument ´last_dump´ is empty, fetch the last data and store
    the ´LAST_DUMP´ timestamp into a file for next calls;
    Otherwise, fetch data since the given (stringified) timestamp

    index -> time,
    columns=["price", "volume", "buy-sell", "market-limit", "vwap"]
    """

    if last_dump is None:
        global LAST_DUMP
        if not LAST_DUMP:
            if os.path.isfile(conf.LAST_DUMP_FILE):
                with open(conf.LAST_DUMP_FILE, "r") as f:
                    LAST_DUMP = f.readline()

    res = doRequest("Trades", {
        "pair": conf.ASSET_PAIR,
        "since": LAST_DUMP
    })

    if last_dump is None:
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
