"""
TODO
"""

from enum import Enum


class ActionEnum(Enum):
    """TODO"""
    HODL = 0
    BUY = 1
    SELL = -1
    DEPOSIT = 2
    WITHDRAW = -2
    FEE = -3


class QuoteEnum(Enum):
    """TODO"""
    CAD = 1
    EUR = 2
    GBP = 3
    JPY = 4
    USD = 5


class CryptoEnum(Enum):
    """TODO"""
    ETC = -1
    ETH = -2
    LTC = -3
    REP = -4
    XBT = -5
    XLM = -6
    XMR = -7
    XRP = -8
    ZEC = -9


class TradeEnum(Enum):
    """TODO"""
    HODL = 0

    BUY_ETC = 1
    BUY_ETH = 2
    BUY_LTC = 3
    BUY_REP = 4
    BUY_XBT = 5
    BUY_XLM = 6
    BUY_XMR = 7
    BUY_XRP = 8
    BUY_ZEC = 9

    SELL_ETC = -1
    SELL_ETH = -2
    SELL_LTC = -3
    SELL_REP = -4
    SELL_XBT = -5
    SELL_XLM = -6
    SELL_XMR = -7
    SELL_XRP = -8
    SELL_ZEC = -9


def floatToTrade(f):
    """TODO"""
    return round(f)  # TODO: round to HODL if too outside MIN_PROBA


def cryptoAndActionTotrade(crypto_enum_val, action_enum_val):
    """TODO"""
    return crypto_enum_val * action_enum_val * -1


def tradeToAction(trade_enum_val):
    """TODO"""
    return trade_enum_val / abs(trade_enum_val)


def tradeToCrypto(trade_enum_val):
    """TODO"""
    return abs(trade_enum_val) * -1
