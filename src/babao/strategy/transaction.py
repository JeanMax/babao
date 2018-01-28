"""
Buy/Sell strategy
"""

import babao.config as conf
import babao.utils.file as fu
import babao.utils.log as log
import babao.data.ledger as ledger

LAST_TX = None
MIN_BAL = 50  # maximum drawdown  # TODO: this should be a percent of... hmm
MIN_PROBA = 1e-2

# LABELS = {"buy": -1, "hold": 0, "sell": 1}


def initLastTransaction(readFile=True):
    """Initialize last transaction price"""

    global LAST_TX

    try:
        if not readFile:
            raise FileNotFoundError("Just use default value!")
        ledger_data = fu.getLastRows(conf.DB_FILE, conf.LEDGER_FRAME, 1)
        LAST_TX = {
            "time": ledger_data.index[0],
            "type": ledger_data.at[ledger_data.index[0], "type"],
            "price": ledger_data.at[ledger_data.index[0], "price"]
        }
    except (FileNotFoundError, IndexError):
        LAST_TX = {"time": None, "type": "s", "price": None}


def gameOver(price):
    """Check if you're broke"""

    return bool(
        ledger.BALANCE["crypto"] * price + ledger.BALANCE["quote"]
        < MIN_BAL
    )


def _tooSoon(timestamp):
    """TODO"""

    if LAST_TX["time"] \
            and timestamp - LAST_TX["time"] \
            < 3 * conf.TIME_INTERVAL * 60 * 10**9:
        if ledger.VERBOSE:
            log.warning("Previous transaction was too soon, waiting")
        return True
    return False


def _canBuy():
    """TODO"""

    if LAST_TX["type"] == "b":
        return False
    if ledger.BALANCE["quote"] < MIN_BAL:
        log.warning("Not enough quote to buy (aka: You're broke :/)")
        return False
    return True


def _canSell():
    """TODO"""

    if LAST_TX["type"] == "s":
        return False
    if ledger.BALANCE["crypto"] < 0.002:
        # TODO: this can be quite high actually
        # support.kraken.com/ \
        # hc/en-us/articles/205893708-What-is-the-minimum-order-size-
        log.warning("Not enough crypto to sell")
        return False
    return True


def buyOrSell(target, price, timestamp):
    """
    Decide wether to buy or sell based on the given ´target´

    It will consider the current ´ledger.BALANCE´, and evenutally update it.
    """

    global LAST_TX

    if target > MIN_PROBA:  # SELL
        if not _canSell() or _tooSoon(timestamp):
            return False
        ledger.logSell(
            ledger.BALANCE["crypto"],
            price,
            crypto_fee=ledger.BALANCE["crypto"] / 100,  # 1% fee
            timestamp=timestamp
        )
        LAST_TX["type"] = "s"

    elif target < -MIN_PROBA:  # BUY
        if not _canBuy() or _tooSoon(timestamp):  # I can english tho
            return False
        ledger.logBuy(
            ledger.BALANCE["quote"],
            price,
            quote_fee=ledger.BALANCE["quote"] / 100,  # 1% fee
            timestamp=timestamp
        )
        LAST_TX["type"] = "b"

    LAST_TX["price"] = price
    LAST_TX["time"] = timestamp

    return True
