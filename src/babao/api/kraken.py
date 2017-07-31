"""Kraken market api methods"""

import time
import http
import socket
import krakenex
import pandas as pd

import babao.config as conf
import babao.utils.log as log

K = krakenex.API()
C = krakenex.Connection()


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
            log.warning("Network error while querying Kraken API!\n" + repr(e))
        except http.client.CannotSendRequest as e:
            log.warning(
                "http.client error while querying Kraken API!"
                + "Restarting connection..."
                + repr(e)
            )
            C.close()
            C = krakenex.Connection()
        except ValueError as e:
            log.warning("ValueError while querying Kraken API!\n" + repr(e))
        # except Exception as e:
            # log.warning("Exception while querying Kraken API!\n" + repr(e))
        else:
            err = res.get("error", [])
            if err:
                for e in err:
                    log.warning("Exception returned by Kraken API!\n" + e)
            else:
                return res["result"]
        log.debug("Connection fail #" + str(fail_counter))
        fail_counter += 1
        time.sleep(0.5)


def getBalance():
    """Return account balance (associatives arrays, keys = assets)"""

    res = doRequest("Balance")
    return res


def getRawTrades(since):
    """
    Fetch last trades from api since the given (stringified) timestamp

    Return a tuple (DataFrame(raw_data), str(last_timestamp))

    index -> time,
    columns=["price", "volume", "buy-sell", "market-limit", "vwap"]
    """

    res = doRequest("Trades", {
        "pair": conf.ASSET_PAIR,
        "since": since
    })

    raw_data = pd.DataFrame(
        res[conf.ASSET_PAIR],
        # not conf.RAW_COLUMNS, this is specific to kraken
        columns=["price", "volume", "time", "buy-sell", "market-limit", "misc"],
        dtype=float  # TODO: dtypes: object(2) (replace bsml letters with 0/1?)
    )
    raw_data.index = (raw_data["time"] * 10**6).astype(int)
    del raw_data["misc"]
    # del raw_data ["market-limit"]  # TODO: this could be useful
    # del raw_data["buy-sell"]  # TODO: this could be useful
    del raw_data["time"]

    # we'll need this later for resampling
    raw_data["vwap"] = raw_data["price"] * raw_data["volume"]

    return raw_data, res["last"]
