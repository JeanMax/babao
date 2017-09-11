"""Handle money related stuffs"""

import time
import pandas as pd

import babao.config as conf
import babao.utils.log as log
import babao.utils.fileutils as fu
# import babao.api as api

# BALANCE = api.getBalance()  # TODO: only fetch info if in bot-mode
BALANCE = {"crypto": 0, "quote": 0}


def initBalance():
    """Init ´BALANCE´ global var"""

    global BALANCE

    try:
        last_ledger = fu.getLastRows(conf.DB_FILE, conf.LEDGER_FRAME, 1)
        BALANCE["crypto"] = float(last_ledger["crypto_bal"])
        BALANCE["quote"] = float(last_ledger["quote_bal"])
    except (FileNotFoundError, KeyError):
        log.warning("No ledger file found.")


def _logTransaction(led_dic, write_to_file=True, timestamp=None):
    """
    Log transaction in a csv ledger file

    ´led_dic´ is a dict with keys == conf.RAW_LEDGER_COLUMNS
    if ´write_to_file´ is True, write entry to conf.LEDGER_FILE
    if ´timestamp´ is not given, the current time will be used
    """

    if timestamp is None:
        timestamp = int(time.time() * 1e6)
    global BALANCE
    led_dic["crypto_bal"] = BALANCE["crypto"] + led_dic.get("crypto_vol", 0)
    led_dic["quote_bal"] = BALANCE["quote"] + led_dic.get("quote_vol", 0)
    BALANCE["crypto"] = led_dic["crypto_bal"]
    BALANCE["quote"] = led_dic["quote_bal"]

    led_df = pd.DataFrame(
        led_dic,
        columns=conf.RAW_LEDGER_COLUMNS,
        index=[timestamp]
    ).fillna(0)

    for c in led_df.columns:
        if c != "type":
            led_df[c] = led_df[c].astype(float)

    if write_to_file:  # TODO
        fu.write(conf.DB_FILE, conf.LEDGER_FRAME, led_df)

    return led_df


def logBuy(quote_vol, price, crypto_fee=0, quote_fee=0, timestamp=None):
    """
    Log a buy transaction (quote -> crypto)

    ´quote_vol´ quantity spent in quote (including fees)
    """

    _logTransaction(
        {
            "type": "b",
            "price": price,
            "crypto_fee": crypto_fee,
            "quote_fee": quote_fee,
            "crypto_vol": (quote_vol - quote_fee - crypto_fee * price) / price,
            "quote_vol": -quote_vol
        },
        timestamp=timestamp
    )
    log.log("Bought for " + str(quote_vol) + " quote @ " + str(price))


def logSell(crypto_vol, price, crypto_fee=0, quote_fee=0, timestamp=None):
    """
    Log a sell transaction (crypto -> quote)

    ´crypto_vol´ quantity spent in crypto (including fees)
    """

    _logTransaction(
        {
            "type": "s",
            "price": price,
            "crypto_fee": crypto_fee,
            "quote_fee": quote_fee,
            "crypto_vol": -crypto_vol,
            "quote_vol": (crypto_vol - crypto_fee - quote_fee / price) * price
        },
        timestamp=timestamp
    )
    log.log("Sold for " + str(crypto_vol) + " crypto @ " + str(price))


def logCryptoDeposit(crypto_vol, crypto_fee=0, timestamp=None):
    """Log a crypto deposit transaction (wallet -> market)"""

    _logTransaction(
        {
            "type": "d",
            "crypto_vol": crypto_vol,
            "crypto_fee": crypto_fee
        },
        timestamp=timestamp
    )


def logCryptoWithdraw(crypto_vol, crypto_fee=0, timestamp=None):
    """Log a crypto withdraw transaction (market -> wallet)"""

    _logTransaction(
        {
            "type": "w",
            "crypto_vol": -crypto_vol,
            "crypto_fee": crypto_fee
        },
        timestamp=timestamp
    )


def logQuoteDeposit(quote_vol, quote_fee=0, timestamp=None):
    """Log a quote deposit transaction (bank -> market)"""

    _logTransaction(
        {
            "type": "d",
            "quote_vol": quote_vol,
            "quote_fee": quote_fee
        },
        timestamp=timestamp
    )


def logQuoteWithdraw(quote_vol, quote_fee=0, timestamp=None):
    """Log a quote withdraw transaction (market -> bank)"""

    _logTransaction(
        {
            "type": "w",
            "quote_vol": -quote_vol,
            "quote_fee": quote_fee
        },
        timestamp=timestamp
    )
