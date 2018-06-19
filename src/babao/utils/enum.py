"""
TODO
"""

from enum import Enum


class ActionEnum(Enum):
    HODL = 0
    BUY = 1
    SELL = -1
    DEPOSIT = 2
    WITHDRAW = -2
    FEE = -3


class QuoteEnum(Enum):
    CAD = 1
    EUR = 2
    GBP = 3
    JPY = 4
    USD = 5


class CryptoEnum(Enum):
    ETC = -1
    ETH = -2
    LTC = -3
    REP = -4
    XBT = -5
    XLM = -6
    XMR = -7
    XRP = -8
    ZEC = -9
