"""
TODO
"""

from babao.inputs.trades.krakenTradesInputBase import ABCKrakenTradesInput
from babao.utils.enum import CryptoEnum, QuoteEnum


# import sys
# for quote in QuoteEnum:
#     for crypto in CryptoEnum:
#         pair = "X" + crypto.name + "Z" + quote.name
#         cls = "KrakenTrades" + pair + "Input"
#         setattr(
#             sys.modules[__name__],
#             cls,
#             type(cls, (ABCKrakenTradesInput,), {
#                 "pair": pair,
#                 "quote": quote,
#                 "crypto": crypto
#             })
#         )


# ###################################### CAD ################################# #

class KrakenTradesXETCZCADInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XETCZCAD"
    quote = QuoteEnum.CAD
    crypto = CryptoEnum.ETC


class KrakenTradesXETHZCADInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XETHZCAD"
    quote = QuoteEnum.CAD
    crypto = CryptoEnum.ETH


class KrakenTradesXLTCZCADInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XLTCZCAD"
    quote = QuoteEnum.CAD
    crypto = CryptoEnum.LTC


class KrakenTradesXREPZCADInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XREPZCAD"
    quote = QuoteEnum.CAD
    crypto = CryptoEnum.REP


class KrakenTradesXXBTZCADInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XXBTZCAD"
    quote = QuoteEnum.CAD
    crypto = CryptoEnum.XBT


class KrakenTradesXXLMZCADInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XXLMZCAD"
    quote = QuoteEnum.CAD
    crypto = CryptoEnum.XLM


class KrakenTradesXXMRZCADInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XXMRZCAD"
    quote = QuoteEnum.CAD
    crypto = CryptoEnum.XMR


class KrakenTradesXXRPZCADInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XXRPZCAD"
    quote = QuoteEnum.CAD
    crypto = CryptoEnum.XRP


class KrakenTradesXZECZCADInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XZECZCAD"
    quote = QuoteEnum.CAD
    crypto = CryptoEnum.ZEC


# ###################################### EUR ################################# #

class KrakenTradesBCHEURInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "BCHEUR"
    quote = QuoteEnum.EUR
    crypto = CryptoEnum.BCH


class KrakenTradesDASHEURInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "DASHEUR"
    quote = QuoteEnum.EUR
    crypto = CryptoEnum.DASH


class KrakenTradesEOSEURInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "EOSEUR"
    quote = QuoteEnum.EUR
    crypto = CryptoEnum.EOS


class KrakenTradesGNOEURInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "GNOEUR"
    quote = QuoteEnum.EUR
    crypto = CryptoEnum.GNO


class KrakenTradesXETCZEURInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XETCZEUR"
    quote = QuoteEnum.EUR
    crypto = CryptoEnum.ETC


class KrakenTradesXETHZEURInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XETHZEUR"
    quote = QuoteEnum.EUR
    crypto = CryptoEnum.ETH


class KrakenTradesXLTCZEURInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XLTCZEUR"
    quote = QuoteEnum.EUR
    crypto = CryptoEnum.LTC


class KrakenTradesXREPZEURInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XREPZEUR"
    quote = QuoteEnum.EUR
    crypto = CryptoEnum.REP


class KrakenTradesXXBTZEURInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XXBTZEUR"
    quote = QuoteEnum.EUR
    crypto = CryptoEnum.XBT


class KrakenTradesXXLMZEURInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XXLMZEUR"
    quote = QuoteEnum.EUR
    crypto = CryptoEnum.XLM


class KrakenTradesXXMRZEURInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XXMRZEUR"
    quote = QuoteEnum.EUR
    crypto = CryptoEnum.XMR


class KrakenTradesXXRPZEURInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XXRPZEUR"
    quote = QuoteEnum.EUR
    crypto = CryptoEnum.XRP


class KrakenTradesXZECZEURInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XZECZEUR"
    quote = QuoteEnum.EUR
    crypto = CryptoEnum.ZEC


# ###################################### GBP ################################# #

class KrakenTradesXETCZGBPInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XETCZGBP"
    quote = QuoteEnum.GBP
    crypto = CryptoEnum.ETC


class KrakenTradesXETHZGBPInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XETHZGBP"
    quote = QuoteEnum.GBP
    crypto = CryptoEnum.ETH


class KrakenTradesXLTCZGBPInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XLTCZGBP"
    quote = QuoteEnum.GBP
    crypto = CryptoEnum.LTC


class KrakenTradesXREPZGBPInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XREPZGBP"
    quote = QuoteEnum.GBP
    crypto = CryptoEnum.REP


class KrakenTradesXXBTZGBPInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XXBTZGBP"
    quote = QuoteEnum.GBP
    crypto = CryptoEnum.XBT


class KrakenTradesXXLMZGBPInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XXLMZGBP"
    quote = QuoteEnum.GBP
    crypto = CryptoEnum.XLM


class KrakenTradesXXMRZGBPInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XXMRZGBP"
    quote = QuoteEnum.GBP
    crypto = CryptoEnum.XMR


class KrakenTradesXXRPZGBPInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XXRPZGBP"
    quote = QuoteEnum.GBP
    crypto = CryptoEnum.XRP


class KrakenTradesXZECZGBPInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XZECZGBP"
    quote = QuoteEnum.GBP
    crypto = CryptoEnum.ZEC


# ###################################### JPY ################################# #

class KrakenTradesXETCZJPYInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XETCZJPY"
    quote = QuoteEnum.JPY
    crypto = CryptoEnum.ETC


class KrakenTradesXETHZJPYInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XETHZJPY"
    quote = QuoteEnum.JPY
    crypto = CryptoEnum.ETH


class KrakenTradesXLTCZJPYInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XLTCZJPY"
    quote = QuoteEnum.JPY
    crypto = CryptoEnum.LTC


class KrakenTradesXREPZJPYInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XREPZJPY"
    quote = QuoteEnum.JPY
    crypto = CryptoEnum.REP


class KrakenTradesXXBTZJPYInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XXBTZJPY"
    quote = QuoteEnum.JPY
    crypto = CryptoEnum.XBT


class KrakenTradesXXLMZJPYInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XXLMZJPY"
    quote = QuoteEnum.JPY
    crypto = CryptoEnum.XLM


class KrakenTradesXXMRZJPYInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XXMRZJPY"
    quote = QuoteEnum.JPY
    crypto = CryptoEnum.XMR


class KrakenTradesXXRPZJPYInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XXRPZJPY"
    quote = QuoteEnum.JPY
    crypto = CryptoEnum.XRP


class KrakenTradesXZECZJPYInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XZECZJPY"
    quote = QuoteEnum.JPY
    crypto = CryptoEnum.ZEC


# ###################################### USD ################################# #

class KrakenTradesBCHUSDInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "BCHUSD"
    quote = QuoteEnum.USD
    crypto = CryptoEnum.BCH


class KrakenTradesDASHUSDInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "DASHUSD"
    quote = QuoteEnum.USD
    crypto = CryptoEnum.DASH


class KrakenTradesEOSUSDInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "EOSUSD"
    quote = QuoteEnum.USD
    crypto = CryptoEnum.EOS


class KrakenTradesGNOUSDInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "GNOUSD"
    quote = QuoteEnum.USD
    crypto = CryptoEnum.GNO


class KrakenTradesXETCZUSDInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XETCZUSD"
    quote = QuoteEnum.USD
    crypto = CryptoEnum.ETC


class KrakenTradesXETHZUSDInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XETHZUSD"
    quote = QuoteEnum.USD
    crypto = CryptoEnum.ETH


class KrakenTradesXLTCZUSDInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XLTCZUSD"
    quote = QuoteEnum.USD
    crypto = CryptoEnum.LTC


class KrakenTradesXREPZUSDInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XREPZUSD"
    quote = QuoteEnum.USD
    crypto = CryptoEnum.REP


class KrakenTradesXXBTZUSDInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XXBTZUSD"
    quote = QuoteEnum.USD
    crypto = CryptoEnum.XBT


class KrakenTradesXXLMZUSDInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XXLMZUSD"
    quote = QuoteEnum.USD
    crypto = CryptoEnum.XLM


class KrakenTradesXXMRZUSDInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XXMRZUSD"
    quote = QuoteEnum.USD
    crypto = CryptoEnum.XMR


class KrakenTradesXXRPZUSDInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XXRPZUSD"
    quote = QuoteEnum.USD
    crypto = CryptoEnum.XRP


class KrakenTradesXZECZUSDInput(ABCKrakenTradesInput):
    """TODO"""
    pair = "XZECZUSD"
    quote = QuoteEnum.USD
    crypto = CryptoEnum.ZEC
