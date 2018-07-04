"""
TODO
Buy/Sell strategy
"""

import re

import babao.config as conf
import babao.utils.log as log
import babao.utils.date as du
import babao.inputs.trades.krakenTradesInput as tra

MIN_BAL = 50  # maximum drawdown  # TODO: this should be a percent of... hmm
MIN_PROBA = 1e-2

LEDGERS = None
TRADES = None  # TODO: all prices are going to be desync in simulation


def initLedgers(simulate=True, log_to_file=True):
    """TODO"""
    global LEDGERS
    global TRADES

    if simulate:
        import babao.inputs.ledger.fakeLedgerInput as led
    else:
        import babao.inputs.ledger.krakenLedgerInput as led

    pat = ".*(" + conf.QUOTE.name + "|" + "|".join(
        [c.name for c in conf.CRYPTOS]
    ) + ")"
    ledgers = [
        led.__dict__[k]() for k in led.__dict__ if re.match(pat, k)
    ]

    if simulate and sum([l.balance for l in ledgers]) == 0:
        ledgers[0].deposit(ledgers[0].__class__(log_to_file=False), 100)
        for i, l in enumerate(ledgers):
            l.log_to_file = log_to_file
            if i != 0:
                l.deposit(l.__class__(log_to_file=False), 0)

    LEDGERS = {l.asset: l for l in ledgers}
    TRADES = {
        l.asset: tra.__dict__[next(
            k for k in tra.__dict__
            if l.asset.name in k and conf.QUOTE.name in k
        )]() for l in ledgers[1:]
    }


def getBalanceInQuote(crypto_enum):
    """TODO"""
    return LEDGERS[crypto_enum].balance * TRADES[crypto_enum].last_row.price


def getGlobalBalanceInQuote():
    """TODO"""
    return sum(
        (getBalanceInQuote(c) for c in TRADES)
    ) + LEDGERS[conf.QUOTE].balance


def getLastTx():
    """TODO"""
    return max((l.last_tx for l in LEDGERS.values()))


def gameOver():
    """Check if you're broke"""
    return getGlobalBalanceInQuote() < MIN_BAL


def _tooSoon(timestamp):
    """
    Check if the previous transaction was too soon to start another one

    The delay is based on conf.TIME_INTERVAL.
    """

    last_tx = getLastTx()
    if last_tx > 0 \
       and timestamp - last_tx < du.secToNano(3 * conf.TIME_INTERVAL * 60):
        if LEDGERS["crypto"].verbose:
            log.warning("Previous transaction was too soon, waiting")
        return True
    return False


def _canBuy():
    """
    TODO
    Check if you can buy crypto

    This is based on your balance and your current position.
    """

    # if LAST_TX["type"] == "b":
    #     return False
    if LEDGERS[conf.QUOTE].balance < MIN_BAL:
        log.warning("Not enough quote to buy (aka: You're broke :/)")
        return False
    return True


def _canSell(crypto_enum):
    """
    Check if you can sell crypto

    This is based on your balance and your current position.
    """

    # if LAST_TX["type"] == "s":
    #     return False
    if getBalanceInQuote(crypto_enum) < MIN_BAL:
        # TODO: this can be quite high actually
        # support.kraken.com/ \
        # hc/en-us/articles/205893708-What-is-the-minimum-order-size-
        log.warning("Not enough crypto to sell")
        return False
    return True


def buy(crypto_enum, volume):
    """TODO"""
    timestamp = du.getTime()
    if not _canBuy() or _tooSoon(timestamp):  # I can english tho
        return False
    LEDGERS[conf.QUOTE].buy(
        LEDGERS[crypto_enum],
        volume,
        TRADES[crypto_enum].last_row.price,
        timestamp
    )
    return True


def sell(crypto_enum, volume):
    """TODO"""
    timestamp = du.getTime()
    if not _canSell(crypto_enum) or _tooSoon(timestamp):
        return False
    LEDGERS[conf.QUOTE].sell(
        LEDGERS[crypto_enum],
        volume,
        TRADES[crypto_enum].last_row.price,
        timestamp
    )
    return True


def buyOrSell(target, crypto_enum):
    """
    Decide wether to buy or sell based on the given ´target´

    It will consider the current ´ledger.BALANCE´, and evenutally update it.
    TODO
    """

    # trade_enum = enu.floatToTradeEnum(target)
    # if trade_enum == enu.TradeEnum.HODL:
    #     return True
    # action_enum = enu.tradeEnumToActionEnum(trade_enum)
    # crypto_enum = enu.tradeEnumToCryptoEnum(trade_enum)

    # TODO: change that ugly target
    # LABELS = {"buy": -1, "hold": 0, "sell": 1}
    if target > MIN_PROBA:  # SELL
        return sell(crypto_enum, LEDGERS[crypto_enum].balance)
    elif target < -MIN_PROBA:  # BUY
        return buy(crypto_enum, LEDGERS[conf.QUOTE].balance)
    return True
