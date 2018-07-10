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
    BCH = -1
    DASH = -2
    EOS = -3
    GNO = -4
    ETC = -5
    ETH = -6
    LTC = -7
    REP = -8
    XBT = -9
    XLM = -10
    XMR = -11
    XRP = -12
    ZEC = -13


class TradeEnum(Enum):
    """TODO"""
    HODL = 0

    BUY_BCH = 1
    BUY_DASH = 2
    BUY_EOS = 3
    BUY_GNO = 4
    BUY_ETC = 5
    BUY_ETH = 6
    BUY_LTC = 7
    BUY_REP = 8
    BUY_XBT = 9
    BUY_XLM = 10
    BUY_XMR = 11
    BUY_XRP = 12
    BUY_ZEC = 13

    SELL_BCH = -1
    SELL_DASH = -2
    SELL_EOS = -3
    SELL_GNO = -4
    SELL_ETC = -5
    SELL_ETH = -6
    SELL_LTC = -7
    SELL_REP = -8
    SELL_XBT = -9
    SELL_XLM = -10
    SELL_XMR = -11
    SELL_XRP = -12
    SELL_ZEC = -13


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
