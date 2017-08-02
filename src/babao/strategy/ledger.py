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
        last_ledger = fu.getLastLines(
            conf.RAW_LEDGER_FILE,
            1,
            conf.RAW_LEDGER_COLUMNS
        )
        BALANCE["crypto"] = float(last_ledger["crypto_bal"])
        BALANCE["quote"] = float(last_ledger["quote_bal"])
    except FileNotFoundError:
        log.warning("No ledger file found.")


def _logTransaction(led_dic, write_to_file=True):
    """
    Log transaction in a csv ledger file

    ´led_dic´ is a dict with keys == conf.RAW_LEDGER_COLUMNS
    if ´write_to_file´ is True, write entry to conf.LEDGER_FILE
    """

    global BALANCE
    led_dic["crypto_bal"] = BALANCE["crypto"] + led_dic.get("crypto_vol", 0)
    led_dic["quote_bal"] = BALANCE["quote"] + led_dic.get("quote_vol", 0)
    BALANCE["crypto"] = led_dic["crypto_bal"]
    BALANCE["quote"] = led_dic["quote_bal"]

    led_df = pd.DataFrame(
        led_dic,
        columns=conf.RAW_LEDGER_COLUMNS,
        index=[int(time.time() * 1e6)]
    ).fillna(0)

    if write_to_file:
        for f in [conf.RAW_LEDGER_FILE, conf.UNSAMPLED_LEDGER_FILE]:
            fu.writeFile(f, led_df, mode="a")

    return led_df


def logBuy(quote_vol, price, crypto_fee=0, quote_fee=0):
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
        }
    )
    log.log("Bought for " + str(quote_vol) + " quote @ " + str(price))


def logSell(crypto_vol, price, crypto_fee=0, quote_fee=0):
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
        }
    )
    log.log("Sold for " + str(crypto_vol) + " crypto @ " + str(price))


def logCryptoDeposit(crypto_vol, crypto_fee=0):
    """Log a crypto deposit transaction (wallet -> market)"""

    _logTransaction(
        {
            "type": "d",
            "crypto_vol": crypto_vol,
            "crypto_fee": crypto_fee
        }
    )


def logCryptoWithdraw(crypto_vol, crypto_fee=0):
    """Log a crypto withdraw transaction (market -> wallet)"""

    _logTransaction(
        {
            "type": "w",
            "crypto_vol": -crypto_vol,
            "crypto_fee": crypto_fee
        }
    )


def logQuoteDeposit(quote_vol, quote_fee=0):
    """Log a quote deposit transaction (bank -> market)"""

    _logTransaction(
        {
            "type": "d",
            "quote_vol": quote_vol,
            "quote_fee": quote_fee
        }
    )


def logQuoteWithdraw(quote_vol, quote_fee=0):
    """Log a quote withdraw transaction (market -> bank)"""

    _logTransaction(
        {
            "type": "w",
            "quote_vol": -quote_vol,
            "quote_fee": quote_fee
        }
    )
