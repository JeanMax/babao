"""
Buy/Sell strategy

This whole shit is temporary, don't worry
"""

import babao.config as conf
import babao.utils.fileutils as fu
import babao.utils.log as log
import babao.data.ledger as ledger

LAST_TRANSACTION_PRICE = None
LAST_TRANSACTION_TIME = None
LOOK_BACK = 42  # TODO
REQUIRED_COLUMNS = ["close"]


def initLastTransactionPrice():
    """Initialize last transaction price"""

    global LAST_TRANSACTION_PRICE
    global LAST_TRANSACTION_TIME

    try:
        df = fu.getLastLines(
            conf.RAW_LEDGER_FILE,
            1,
            conf.RAW_LEDGER_COLUMNS
        )
        LAST_TRANSACTION_TIME = df.index[0]
        LAST_TRANSACTION_PRICE = df.at[df.index[0], "price"]
    except FileNotFoundError:
        LAST_TRANSACTION_PRICE = 0
        LAST_TRANSACTION_TIME = 0


def minSellPrice():
    """
    Return the minimum price to sell coins and make profit

    Based on the last transaction price and transaction fee
    """

    if LAST_TRANSACTION_PRICE > 0:
        # +1% for transaction cost/delay
        # +4% for moneyz
        return LAST_TRANSACTION_PRICE + LAST_TRANSACTION_PRICE * 0.05
    return -1


def maxBuyPrice():
    """
    Return the maximum price to buy coins and make profit

    Based on the last transaction price and transaction fee
    """

    if LAST_TRANSACTION_PRICE > 0:
        # -1% for transaction cost/delay
        # -4% for moneyz
        return LAST_TRANSACTION_PRICE - LAST_TRANSACTION_PRICE * 0.05
    return 1 << 16


def analyse(sample_data):
    """Just a dummy strategy"""

    # TODO: 0 is hardcoded "close" column location... (iat is realllly faster)
    current_price = sample_data.iat[-1, 0]
    i = sample_data.index[-1]

    global LAST_TRANSACTION_PRICE
    global LAST_TRANSACTION_TIME

    if ledger.BALANCE["crypto"] > 0.001:
        if current_price > minSellPrice():
            ledger.logSell(
                ledger.BALANCE["crypto"],
                current_price,
                crypto_fee=ledger.BALANCE["crypto"] / 100,  # 1% fee
                timestamp=i
            )
            LAST_TRANSACTION_PRICE = current_price
            LAST_TRANSACTION_TIME = i
    else:
        if i - LAST_TRANSACTION_TIME > 604800000000:
            log.warning("Transaction failed (1 week) :/")
            LAST_TRANSACTION_PRICE = 0
            LAST_TRANSACTION_TIME = 0
        if current_price < maxBuyPrice():
            ledger.logBuy(
                ledger.BALANCE["quote"],
                current_price,
                quote_fee=ledger.BALANCE["quote"] / 100,  # 1% fee
                timestamp=i
            )
            LAST_TRANSACTION_PRICE = current_price
            LAST_TRANSACTION_TIME = i
