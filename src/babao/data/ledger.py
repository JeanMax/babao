"""Handle money related stuffs"""

import time
import pandas as pd

import babao.config as conf
import babao.utils.log as log
import babao.utils.file as fu
# import babao.api as api

# BALANCE = api.getBalance()  # TODO: only fetch info if in bot-mode
BALANCE = {"crypto": 0, "quote": 0}
LOG_TO_FILE = True
VERBOSE = False


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
        last_ledger = fu.getLastRows(conf.DB_FILE, conf.LEDGER_FRAME, 1)
        BALANCE["crypto"] = float(last_ledger["crypto_bal"])
        BALANCE["quote"] = float(last_ledger["quote_bal"])
    except (FileNotFoundError, KeyError):
        log.warning("No ledger file found.")


def setLog(enable_file_logging=True):
    """Set the ´LOG_TO_FILE´ global var"""

    global LOG_TO_FILE
    LOG_TO_FILE = enable_file_logging


def setVerbose(enable_verbose=True):
    """Set the ´VERBOSE´ global var"""

    global VERBOSE
    VERBOSE = enable_verbose


def _logTransaction(led_dic, timestamp=None):
    """
    Log transaction in a csv ledger file

    ´led_dic´ is a dict with keys == conf.RAW_LEDGER_COLUMNS
    if ´timestamp´ is not given, the current time will be used
    """

    if timestamp is None:
        timestamp = int(time.time() * 1e6)
    global BALANCE
    led_dic["crypto_bal"] = BALANCE["crypto"] + led_dic.get("crypto_vol", 0)
    led_dic["quote_bal"] = BALANCE["quote"] + led_dic.get("quote_vol", 0)
    BALANCE["crypto"] = round(led_dic["crypto_bal"], 9)
    BALANCE["quote"] = round(led_dic["quote_bal"], 9)

    if LOG_TO_FILE:
        led_df = pd.DataFrame(
            led_dic,
            columns=conf.RAW_LEDGER_COLUMNS,
            index=[timestamp]
        ).fillna(0)

        for c in led_df.columns:
            if c != "type":
                led_df[c] = led_df[c].astype(float)

        fu.write(conf.DB_FILE, conf.LEDGER_FRAME, led_df)


def logBuy(quote_vol, price, crypto_fee=0, quote_fee=0, timestamp=None):
    """
    Log a buy transaction (quote -> crypto)

    ´quote_vol´ quantity spent in quote (including fees)
    """

    if VERBOSE:
        log.info(
            "Bought for", round(quote_vol, 4),
            "crypto @", int(price)
        )

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

    if VERBOSE:
        log.info(
            "Sold for", round(crypto_vol, 4),
            "crypto @", int(price)
        )

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


def printCliFormat():
    """Print ledger with ledger-cli format"""

    def _printHeader(index, tx_type, currency):
        """Print first line of entry (date/description)"""
        print(
            pd.to_datetime(index // 10**6, unit="s"),
            "*",
            tx_type,
            "(" + currency + ")"
        )

    def _printRecipient(rec_name, amount, asset, price=None):
        """Print one line of an entry"""
        left = "\t%s\t\t%f" % (rec_name, amount)
        if price is not None:
            asset = asset + " ; @ " + price  # TODO: price isn't exact
        print(left, asset)

    def _handleFee(crypto_fee, quote_fee):
        """Call _printRecipient on fees if required"""
        if crypto_fee > 0:
            _printRecipient("Expenses:Fee", crypto_fee, conf.ASSET_PAIR[:4])
        if quote_fee > 0:
            _printRecipient("Expenses:Fee", quote_fee, conf.ASSET_PAIR[4:])

    def _handleDeposit(ind, amount, asset, crypto_fee, quote_fee):
        """Do all stuffs needed for deposit"""
        _printHeader(ind, "deposit", asset)
        _printRecipient("Assets:Bank\t", amount * -1, asset)
        _handleFee(crypto_fee, quote_fee)
        _printRecipient("Assets:Market", amount, asset)

    def _handleWithdraw(ind, amount, asset, crypto_fee, quote_fee):
        """Do all stuffs needed for withdraw"""
        _printHeader(ind, "withdraw", asset)
        _printRecipient("Assets:Market", amount * -1, asset)
        _handleFee(crypto_fee, quote_fee)
        _printRecipient("Assets:Bank\t", amount, asset)

    raw_ledger = fu.read(
        conf.DB_FILE,
        conf.LEDGER_FRAME
    )

    for i in range(len(raw_ledger)):
        ind = raw_ledger.index[i]

        if raw_ledger.at[ind, "type"] == "d":
            if raw_ledger.at[ind, "crypto_vol"] > 0:
                _handleDeposit(
                    ind,
                    raw_ledger.at[ind, "crypto_vol"],
                    conf.ASSET_PAIR[:4],
                    raw_ledger.at[ind, "crypto_fee"],
                    raw_ledger.at[ind, "quote_fee"]
                )
            else:
                _handleDeposit(
                    ind,
                    raw_ledger.at[ind, "quote_vol"],
                    conf.ASSET_PAIR[4:],
                    raw_ledger.at[ind, "crypto_fee"],
                    raw_ledger.at[ind, "quote_fee"]
                )

        elif raw_ledger.at[ind, "type"] == "w":  # TODO: check sign
            if raw_ledger.at[ind, "crypto_vol"] > 0:
                _handleWithdraw(
                    ind,
                    raw_ledger.at[ind, "crypto_vol"],
                    conf.ASSET_PAIR[:4],
                    raw_ledger.at[ind, "crypto_fee"],
                    raw_ledger.at[ind, "quote_fee"]
                )
            else:
                _handleWithdraw(
                    ind,
                    raw_ledger.at[ind, "quote_vol"],
                    conf.ASSET_PAIR[:4],
                    raw_ledger.at[ind, "crypto_fee"],
                    raw_ledger.at[ind, "quote_fee"]
                )

        elif raw_ledger.at[ind, "type"] == "b":
            _printHeader(
                ind,
                "buy",
                conf.ASSET_PAIR[4:] + " -> " + conf.ASSET_PAIR[:4]
            )
            _printRecipient(
                "Assets:Market",
                raw_ledger.at[ind, "quote_vol"],
                conf.ASSET_PAIR[4:]
            )
            _handleFee(
                raw_ledger.at[ind, "crypto_fee"],
                raw_ledger.at[ind, "quote_fee"]
            )
            _printRecipient(
                "Assets:Market",
                raw_ledger.at[ind, "crypto_vol"],
                conf.ASSET_PAIR[:4],
                "%f %s" % (raw_ledger.at[ind, "price"], conf.ASSET_PAIR[4:])
            )

        elif raw_ledger.at[ind, "type"] == "s":
            _printHeader(
                ind,
                "sell",
                conf.ASSET_PAIR[:4] + " -> " + conf.ASSET_PAIR[4:]
            )
            _printRecipient(
                "Assets:Market",
                raw_ledger.at[ind, "crypto_vol"],
                conf.ASSET_PAIR[:4],
                "%f %s" % (raw_ledger.at[ind, "price"], conf.ASSET_PAIR[4:])
            )
            _handleFee(
                raw_ledger.at[ind, "crypto_fee"],
                raw_ledger.at[ind, "quote_fee"]
            )
            _printRecipient(
                "Assets:Market",
                raw_ledger.at[ind, "quote_vol"],
                conf.ASSET_PAIR[4:]
            )

        print()
