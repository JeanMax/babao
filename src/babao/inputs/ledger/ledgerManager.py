"""
TODO
Buy/Sell strategy
"""

import re
from typing import Optional, Dict, Union, TYPE_CHECKING  # noqa: F401

import babao.config as conf
import babao.inputs.trades.krakenTradesInput as tra
import babao.utils.date as du
import babao.utils.log as log
from babao.utils.enum import ActionEnum, CryptoEnum, QuoteEnum  # noqa: F401

MIN_BAL = 50  # maximum drawdown  # TODO: this should be a percent of... hmm

if TYPE_CHECKING:
    from babao.inputs.ledger.ledgerInputBase import ABCLedgerInput  # noqa: F401
    AssetEnum = Union["CryptoEnum", "QuoteEnum"]

LEDGERS = None  # type: Optional[Dict[AssetEnum, ABCLedgerInput]]
TRADES = None  # type: Optional[Dict[CryptoEnum, ABCLedgerInput]]


def initLedgers(simulate=True, log_to_file=True):
    """TODO"""
    global LEDGERS
    global TRADES

    # TODO: put args.func in a conf global
    if simulate:
        import babao.inputs.ledger.fakeLedgerInput as led
    else:
        import babao.inputs.ledger.krakenLedgerInput as led

    pat = ".*(" + conf.QUOTE.name + "|" + "|".join(
        [c.name for c in conf.CRYPTOS]
    ) + ")"
    ledgers = [
        led.__dict__[k](log_to_file) for k in led.__dict__ if re.match(pat, k)
    ]

    if conf.CURRENT_COMMAND != "fetch" and simulate \
       and sum([l.balance for l in ledgers]) == 0:
        ledgers[0].deposit(ledgers[0].__class__(log_to_file=False), 100)
        for l in ledgers[1:]:
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
    return LEDGERS[crypto_enum].balance * TRADES[crypto_enum].current_row.price


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
        if LEDGERS[conf.QUOTE].verbose:
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
        if LEDGERS[conf.QUOTE].verbose:
            log.warning("Not enough", conf.QUOTE.name, "to buy")
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
        # this can be quite high actually
        # support.kraken.com/ \
        # hc/en-us/articles/205893708-What-is-the-minimum-order-size-
        if LEDGERS[conf.QUOTE].verbose:
            log.warning("Not enough", crypto_enum.name, "to sell")
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
        TRADES[crypto_enum].current_row.price,
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
        TRADES[crypto_enum].current_row.price,
        timestamp
    )
    return True


def buyOrSell(action_enum, crypto_enum, volume=None):
    """
    Decide wether to buy or sell based on the given ´target´

    It will consider the current ´ledger.BALANCE´, and evenutally update it.
    TODO
    """
    if action_enum == ActionEnum.BUY:
        if volume is None:
            volume = LEDGERS[conf.QUOTE].balance
        return buy(crypto_enum, volume)
    if action_enum == ActionEnum.SELL:
        if volume is None:
            volume = LEDGERS[crypto_enum].balance
        return sell(crypto_enum, volume)
    return False
