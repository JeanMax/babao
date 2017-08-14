"""Handle money related stuffs"""

import time
import pandas as pd

import babao.config as conf
import babao.utils.log as log
import babao.utils.fileutils as fu
# import babao.api as api

# BALANCE = api.getBalance()  # TODO: only fetch info if in bot-mode
BALANCE = {"crypto": 0, "quote": 0}
LOG_TO_FILE = True


def initBalance(force=None):
    """
    Init ´BALANCE´ global var

    If the force parameter is given, update ´BALANCE´ with the subfields
    "crypto" and "quote" of the force dict.
    """

    global BALANCE

    if force is not None:
        BALANCE = force
        return

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


def setLog(enable_file_logging):
    """Set the ´LOG_TO_FILE´ global var"""

    global LOG_TO_FILE
    LOG_TO_FILE = enable_file_logging


def _logTransaction(led_dic, timestamp=None):
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

    if LOG_TO_FILE:
        led_df = pd.DataFrame(
            led_dic,
            columns=conf.RAW_LEDGER_COLUMNS,
            index=[timestamp]
        ).fillna(0)

        fu.writeFile(conf.RAW_LEDGER_FILE, led_df, mode="a")


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
