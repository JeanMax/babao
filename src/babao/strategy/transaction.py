"""
Buy/Sell strategy
"""

import babao.config as conf
import babao.utils.log as log
from babao.inputs.ledger.krakenLedgerInput import KrakenLedgerEURInput
from babao.inputs.ledger.krakenLedgerInput import KrakenLedgerXBTInput
from babao.inputs.ledger.fakeLedgerInput import FakeLedgerEURInput
from babao.inputs.ledger.fakeLedgerInput import FakeLedgerXBTInput

MIN_BAL = 50  # maximum drawdown  # TODO: this should be a percent of... hmm
MIN_PROBA = 1e-2

L = None

# LABELS = {"buy": -1, "hold": 0, "sell": 1}


def initLedger(simulate=True):
    global L
    if simulate:
        L = {
            "crypto": FakeLedgerXBTInput(),
            "quote": FakeLedgerEURInput()
        }
        if L["quote"].balance == 0 and L["crypto"].balance == 0:
            L["quote"].deposit(FakeLedgerEURInput(log_to_file=False), 100)
            L["crypto"].deposit(FakeLedgerXBTInput(log_to_file=False), 0)
    else:
        L = {
            "crypto": KrakenLedgerXBTInput(),
            "quote": KrakenLedgerEURInput()
        }


def gameOver(price):
    """Check if you're broke"""

    return bool(
        L["crypto"].balance * price + L["quote"].balance
        < MIN_BAL
    )


def _tooSoon(timestamp):
    """
    Check if the previous transaction was too soon to start another one

    The delay is based on conf.TIME_INTERVAL.
    """

    last_tx = min(L["crypto"].last_tx, L["quote"].last_tx)
    if last_tx > 0 \
       and timestamp - last_tx < 3 * conf.TIME_INTERVAL * 60 * 10**9:
        if L["crypto"].verbose:
            log.warning("Previous transaction was too soon, waiting")
        return True
    return False


def _canBuy():
    """
    Check if you can buy crypto

    This is based on your balance and your current position.
    """

    # if LAST_TX["type"] == "b":
    #     return False
    if L["quote"].balance < MIN_BAL:
        log.warning("Not enough quote to buy (aka: You're broke :/)")
        return False
    return True


def _canSell():
    """
    Check if you can sell crypto

    This is based on your balance and your current position.
    """

    # if LAST_TX["type"] == "s":
    #     return False
    if L["crypto"].balance < 0.002:
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
    TODO
    """

    if target > MIN_PROBA:  # SELL
        if not _canSell() or _tooSoon(timestamp):
            return False
        L["quote"].sell(L["crypto"], L["crypto"].balance, price, timestamp)
    elif target < -MIN_PROBA:  # BUY
        if not _canBuy() or _tooSoon(timestamp):  # I can english tho
            return False
        L["quote"].buy(L["crypto"], L["quote"].balance, price, timestamp)
    return True
