"""Handle money related stuffs"""

import time

import babao.config as conf
import babao.utils.log as log
import babao.utils.fileutils as fu
# import babao.api as api

# BALANCE = api.getBalance()  # TODO: only fetch info if in bot-mode
BALANCE = {"XXBT": 0.0000000000, "ZEUR": 100}  # TODO: config var for pair?
LAST_TRANSACTION_PRICE = None


def initLastTransactionPrice():
    """Initialize last transaction price"""
    global LAST_TRANSACTION_PRICE

    try:
        LAST_TRANSACTION_PRICE = float(
            fu.getLastLines(conf.LEDGER_FILE, 1, names=[
                "time", "price", "volume", "buy-sell", "market-limit"
            ])["price"]
        )
    except FileNotFoundError:
        LAST_TRANSACTION_PRICE = -1


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


def logTransaction(buy_sell, price, volume):
    """
    Log transaction in a csv ledger file

    Format:
    timestamp,price,volume(btc),buy-sell,market-limit
    """

    # TODO: bot-mode only
    if buy_sell == "buy":
        BALANCE["XXBT"] = volume - volume * 0.01
        BALANCE["ZEUR"] = 0
    else:
        BALANCE["ZEUR"] = (volume - volume * 0.01) * price
        BALANCE["XXBT"] = 0

    with open(conf.LEDGER_FILE, "a") as f:
        f.write(
            str(int(time.time())) + ","
            + str(price) + ","
            + str(volume) + ","
            + buy_sell[0] + ","
            + "m" + "\n"
        )

    global LAST_TRANSACTION_PRICE
    LAST_TRANSACTION_PRICE = price

    log.log(
        buy_sell + " " + str(volume) + " @ " + str(price) + "\n"
        + "balance: " + str(BALANCE["XXBT"]) + " BTC / "
        + str(BALANCE["ZEUR"]) + " EUR"
    )
