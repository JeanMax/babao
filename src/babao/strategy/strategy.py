"""
Buy/Sell strategy

This whole shit is temporary, don't worry
"""

import babao.config as conf
import babao.utils.log as log
import babao.utils.fileutils as fu
import babao.strategy.ledger as ledger

LAST_TRANSACTION_PRICE = None


def initLastTransactionPrice():
    """Initialize last transaction price"""

    global LAST_TRANSACTION_PRICE

    try:
        LAST_TRANSACTION_PRICE = float(
            fu.getLastLines(conf.LEDGER_FILE, 1, conf.LEDGER_COLUMNS)["price"]
        )
    except FileNotFoundError:
        LAST_TRANSACTION_PRICE = 0


def minSellPrice():
    """
    Return the minimum price to sell coins and make profit

    Based on the last transaction price and transaction fee
    """

    if not LAST_TRANSACTION_PRICE:
        initLastTransactionPrice()

    if LAST_TRANSACTION_PRICE > 0:
        # +1% for transaction cost/delay
        return LAST_TRANSACTION_PRICE + LAST_TRANSACTION_PRICE * 0.01
    return -1


def maxBuyPrice():
    """
    Return the maximum price to buy coins and make profit

    Based on the last transaction price and transaction fee
    """

    if not LAST_TRANSACTION_PRICE:
        initLastTransactionPrice()

    if LAST_TRANSACTION_PRICE > 0:
        # -1% for transaction cost/delay
        return LAST_TRANSACTION_PRICE - LAST_TRANSACTION_PRICE * 0.01
    return 1 << 16


def analyse():
    """Just a dummy strategy"""

    log.debug("Entering analyse()")

    current_price = float(fu.getLastLines(
        conf.RESAMPLED_FILE,
        1,
        conf.RESAMPLED_COLUMNS
    ).tail(1)["close"])

    global LAST_TRANSACTION_PRICE

    if ledger.BALANCE["crypto"] > 0.001:
        if current_price > minSellPrice():
            ledger.logSell(
                ledger.BALANCE["crypto"],
                current_price,
                crypto_fee=ledger.BALANCE["crypto"] / 100  # 1% fee
            )
            LAST_TRANSACTION_PRICE = current_price
    else:
        if current_price < maxBuyPrice():
            ledger.logBuy(
                ledger.BALANCE["quote"],
                current_price,
                quote_fee=ledger.BALANCE["quote"] / 100  # 1% fee
            )
            LAST_TRANSACTION_PRICE = current_price
