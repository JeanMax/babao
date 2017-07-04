"""TODO"""

import os
import time
import http
import socket
import krakenex
import pandas as pd #TODO: is it imported for EACH file??

import babao.config as conf
import babao.log as log

K = krakenex.API()
K.load_key(conf.API_KEY_FILE)
C = krakenex.Connection()
# krakenex.set_conection(c)
LAST_DUMP = ""

# TODO: block sig INT/TERM

def kraken_getRawTrades():
    global LAST_DUMP
    global C
    if not LAST_DUMP:
        if os.path.isfile(conf.LAST_DUMP_FILE):
            with open(conf.LAST_DUMP_FILE, "r") as f:
                LAST_DUMP = f.readline()

    # we loop in case of request error (503...)
    while True:
        try:
            res = K.query_public("Trades", {
                "pair": conf.ASSET_PAIR,
                "since": LAST_DUMP
            }, C)
        except (socket.timeout, socket.error, http.client.BadStatusLine) as e:
            log.error('Network error while querying Kraken API!\n' + repr(e))
        except http.client.CannotSendRequest as e:
            log.error('http.client error while querying Kraken API!\nRestarting connection...' + repr(e))
            C.close()
            C = krakenex.Connection()
        except ValueError as e:
            log.error('ValueError while querying Kraken API!\n' + repr(e))
        # except Exception as e:
            # log.error('Exception while querying Kraken API!\n' + repr(e))
        else:
            err = res.get('error', [])
            if err:
                for e in err:
                    log.error('Exception returned by Kraken API!\n' + e)
            else:
                break
        time.sleep(0.5)

    LAST_DUMP = res["result"]["last"]
    with open(conf.LAST_DUMP_FILE, "w") as f:
        f.write(LAST_DUMP)


    df = pd.DataFrame(
        res["result"][conf.ASSET_PAIR],
        columns=["price", "volume", "time", "buy-sell", "market-limit", "misc"],
        dtype=float
    )
    df.index = df["time"].astype(int)
    del df["misc"]
    # del df ["market-limit"] # TODO: this could be useful
    # del df["buy-sell"] # TODO: this could be useful
    del df["time"]
    df["vwap"] = df["price"] * df["volume"] # we'll need this later for resampling

    # now it looks like this:
    # index="time", columns=["price", "volume", "buy-sell", "market-limit", "vwap"]

    return df


def dumpData():
    log.debug("Entering dumpData()") # DEBUG

    raw_data = kraken_getRawTrades()
    raw_data.to_csv(conf.RAW_FILE, header=False, mode="a")

    return raw_data
