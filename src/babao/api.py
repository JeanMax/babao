"""TODO"""

import os
import time
import http
import socket
import krakenex
import pandas as pd #TODO: is it imported for EACH file??

import babao.config as conf
import babao.log as log

print("Do you run me only once?") # DEBUG
K = krakenex.API()
K.load_key(conf.API_KEY_FILE)
C = krakenex.Connection()
# krakenex.set_conection(c)
LAST_DUMP = ""

# TODO: block sig INT/TERM

def kraken_getRawTrades():
    last_dump_file = os.path.join(conf.DATA_DIR, conf.ASSET_PAIR + "-last_dump.timestamp")
    global LAST_DUMP
    global C
    if not LAST_DUMP:
        if os.path.isfile(last_dump_file):
            with open(last_dump_file, "r") as f:
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
    with open(last_dump_file, "w") as f:
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

    raw_data_file = os.path.join(conf.DATA_DIR, conf.ASSET_PAIR + "-raw.csv")
    raw_data.to_csv(raw_data_file, header=False, mode="a")

    return raw_data
