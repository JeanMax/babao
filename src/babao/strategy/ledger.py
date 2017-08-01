"""Handle money related stuffs"""

import time
import pandas as pd

import babao.config as conf
import babao.utils.log as log
import babao.utils.fileutils as fu
# import babao.api as api

# BALANCE = api.getBalance()  # TODO: only fetch info if in bot-mode
BALANCE = {"crypto": 0, "quote": 0}


def _logTransaction(ledger):
    """
    Log transaction in a csv ledger file

    ´ledger´ is a dict with keys == conf.LEDGER_COLUMNS
    """

    global BALANCE
    ledger["crypto_bal"] = BALANCE["crypto"] + ledger.get("crypto_vol", 0)
    ledger["quote_bal"] = BALANCE["quote"] + ledger.get("quote_vol", 0)
    BALANCE["crypto"] = ledger["crypto_bal"]
    BALANCE["quote"] = ledger["quote_bal"]

    fu.writeFile(
        conf.LEDGER_FILE,
        pd.DataFrame(
            ledger,
            columns=conf.LEDGER_COLUMNS,
            index=[int(time.time() * 1e6)]
        ).fillna(0),
        mode="a"
    )


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
