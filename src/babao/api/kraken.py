"""Kraken market api methods"""

import time
import http
import socket
import krakenex
import pandas as pd

import babao.config as conf
import babao.utils.log as log
import babao.data.ledger as ledger

K = krakenex.API()


def initKey():
    """Load the api key from config folder"""

    K.load_key(conf.API_KEY_FILE)


def _doRequest(method, req=None):
    """General function for kraken api requests"""

    if not req:
        req = {}

    # we loop in case of request error (503...)
    fail_counter = 1
    while fail_counter > 0:  # really nice loop bro, respect... no goto tho
        try:
            if method == "Trades":
                res = K.query_public(method, req)
            else:
                res = K.query_private(method, req)
        except (
                socket.timeout,
                socket.error,
                http.client.BadStatusLine,
                http.client.CannotSendRequest,
                ValueError
        ) as e:
            log.warning("Network error while querying Kraken API!\n" + repr(e))
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

    return None  # warning-trap


def getBalance():
    """Return account balance (associatives arrays, keys = assets)"""

    res = _doRequest("Balance")
    return res


def getLedger(since):
    """
    Fetch last ledger entries from api since the given (stringified) timestamp

    Transaction will be logged using functions from ledger module
    Return a tuple (numberOfTransactionFetched, str(last_timestamp))
    """

    res = _doRequest("Ledgers", {"start": since})

    if res["count"] == 0:
        return 0

    raw_ledger = pd.DataFrame(res["ledger"]).T
    raw_ledger.index = (raw_ledger["time"] * 1e6).astype(int)
    del raw_ledger["time"]
    del raw_ledger["aclass"]
    raw_ledger = raw_ledger.sort_index()

    raw_ledger = raw_ledger.where(
        (raw_ledger["asset"] == conf.ASSET_PAIR[:4])
        | (raw_ledger["asset"] == conf.ASSET_PAIR[4:])
    )

    raw_ledger["amount"] = raw_ledger["amount"].astype(float)
    raw_ledger["fee"] = raw_ledger["fee"].astype(float)
    raw_ledger["balance"] = raw_ledger["balance"].astype(float)

    for i in range(len(raw_ledger)):
        ind = raw_ledger.index[i]

        if raw_ledger.at[ind, "type"] == "deposit":
            if raw_ledger.at[ind, "asset"] == conf.ASSET_PAIR[:4]:
                ledger.logCryptoDeposit(
                    raw_ledger.at[ind, "amount"],
                    raw_ledger.at[ind, "fee"],
                    ind
                )
            else:
                ledger.logQuoteDeposit(
                    raw_ledger.at[ind, "amount"],
                    raw_ledger.at[ind, "fee"],
                    ind
                )

        elif raw_ledger.at[ind, "type"] == "withdraw":  # TODO: check type str
            # TODO: check if fees should be excluded
            if raw_ledger.at[ind, "asset"] == conf.ASSET_PAIR[:4]:
                ledger.logCryptoWithdraw(
                    raw_ledger.at[ind, "amount"] * -1,  # TODO: check if < 0
                    raw_ledger.at[ind, "fee"],
                    ind
                )
            else:
                ledger.logQuoteWithdraw(
                    raw_ledger.at[ind, "amount"] * -1,  # TODO: check if < 0
                    raw_ledger.at[ind, "fee"],
                    ind
                )

        elif raw_ledger.at[ind, "type"] == "trade":
            if raw_ledger.at[ind, "asset"] == conf.ASSET_PAIR[:4]:
                next_ind = raw_ledger.index[i + 1]
                crypto_vol = abs(raw_ledger.at[ind, "amount"])
                crypto_fee = raw_ledger.at[ind, "fee"]
                quote_vol = abs(raw_ledger.at[next_ind, "amount"])
                quote_fee = raw_ledger.at[next_ind, "fee"]
                price = quote_vol / crypto_vol
                if raw_ledger.at[ind, "amount"] > 0:
                    ledger.logBuy(
                        quote_vol + quote_fee,
                        price,
                        crypto_fee,
                        quote_fee,
                        ind
                    )
                else:
                    ledger.logSell(
                        crypto_vol + crypto_fee,
                        price,
                        crypto_fee,
                        quote_fee,
                        ind
                    )

    return res["count"], str(raw_ledger.index[-1] / 1e6)


def getRawTrades(since):
    """
    Fetch last trades from api since the given (stringified) timestamp

    Return a tuple (DataFrame(raw_data), str(last_timestamp))
    raw_data is formated as specified by conf.RAW_TRADES_COLUMNS
    """

    res = _doRequest("Trades", {
        "pair": conf.ASSET_PAIR,
        "since": since
    })

    raw_data = pd.DataFrame(
        res[conf.ASSET_PAIR],
        # not conf.RAW_TRADES_COLUMNS, this is specific to kraken
        columns=["price", "volume", "time", "buy-sell", "market-limit", "misc"],
        dtype=float  # TODO: dtypes: object(2) (replace bsml letters with 0/1?)
    )
    raw_data.index = (raw_data["time"] * 1e9).astype(int)
    del raw_data["misc"]
    del raw_data["market-limit"]  # TODO: this could be useful
    del raw_data["buy-sell"]  # TODO: this could be useful
    del raw_data["time"]

    return raw_data, res["last"]
