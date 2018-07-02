"""
Buy/Sell strategy
"""

import re

import babao.config as conf
import babao.utils.log as log
import babao.utils.date as du

MIN_BAL = 50  # maximum drawdown  # TODO: this should be a percent of... hmm
MIN_PROBA = 1e-2

L = None

# LABELS = {"buy": -1, "hold": 0, "sell": 1}


def initLedger(simulate=True):
    """TODO"""
    if simulate:
        import babao.inputs.ledger.fakeLedgerInput as led
    else:
        import babao.inputs.ledger.krakenLedgerInput as led

    pat = ".*(" + conf.QUOTE.name + "|" + "|".join(
        [c.name for c in conf.CRYPTOS]
    ) + ")"
    led_filter = filter(lambda s: re.match(pat, s), led.__dict__.keys())
    ledgers = [led.__dict__[k]() for k in led_filter]

    if simulate and sum([l.balance for l in ledgers]) == 0:
        ledgers[0].deposit(ledgers[0].__class__(log_to_file=False), 100)
        for l in ledgers[1:]:
            l.deposit(l.__class__(log_to_file=False), 0)

    global L
    L = dict(zip([l.asset for l in ledgers], ledgers))


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
       and timestamp - last_tx < du.secToNano(3 * conf.TIME_INTERVAL * 60):
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
