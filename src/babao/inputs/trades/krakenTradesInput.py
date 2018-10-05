"""
Concrete class for kraken trade inputs

We could have defined all these with the following commentend out snippet,
but for explicitness reasons we'll keep them this way.
This also allows linter to understand what's going on.
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
    """Kraken trade input for ETC crypto vs CAD quote"""
    pair = "XETCZCAD"
    quote = QuoteEnum.CAD
    crypto = CryptoEnum.ETC


class KrakenTradesXETHZCADInput(ABCKrakenTradesInput):
    """Kraken trade input for ETH crypto vs CAD quote"""
    pair = "XETHZCAD"
    quote = QuoteEnum.CAD
    crypto = CryptoEnum.ETH


class KrakenTradesXLTCZCADInput(ABCKrakenTradesInput):
    """Kraken trade input for LTC crypto vs CAD quote"""
    pair = "XLTCZCAD"
    quote = QuoteEnum.CAD
    crypto = CryptoEnum.LTC


class KrakenTradesXREPZCADInput(ABCKrakenTradesInput):
    """Kraken trade input for REP crypto vs CAD quote"""
    pair = "XREPZCAD"
    quote = QuoteEnum.CAD
    crypto = CryptoEnum.REP


class KrakenTradesXXBTZCADInput(ABCKrakenTradesInput):
    """Kraken trade input for XBT crypto vs CAD quote"""
    pair = "XXBTZCAD"
    quote = QuoteEnum.CAD
    crypto = CryptoEnum.XBT


class KrakenTradesXXLMZCADInput(ABCKrakenTradesInput):
    """Kraken trade input for XLM crypto vs CAD quote"""
    pair = "XXLMZCAD"
    quote = QuoteEnum.CAD
    crypto = CryptoEnum.XLM


class KrakenTradesXXMRZCADInput(ABCKrakenTradesInput):
    """Kraken trade input for XMR crypto vs CAD quote"""
    pair = "XXMRZCAD"
    quote = QuoteEnum.CAD
    crypto = CryptoEnum.XMR


class KrakenTradesXXRPZCADInput(ABCKrakenTradesInput):
    """Kraken trade input for XRP crypto vs CAD quote"""
    pair = "XXRPZCAD"
    quote = QuoteEnum.CAD
    crypto = CryptoEnum.XRP


class KrakenTradesXZECZCADInput(ABCKrakenTradesInput):
    """Kraken trade input for ZEC crypto vs CAD quote"""
    pair = "XZECZCAD"
    quote = QuoteEnum.CAD
    crypto = CryptoEnum.ZEC


# ###################################### EUR ################################# #

class KrakenTradesBCHEURInput(ABCKrakenTradesInput):
    """Kraken trade input for CHE crypto vs R quote"""
    pair = "BCHEUR"
    quote = QuoteEnum.EUR
    crypto = CryptoEnum.BCH


class KrakenTradesDASHEURInput(ABCKrakenTradesInput):
    """Kraken trade input for ASH crypto vs UR quote"""
    pair = "DASHEUR"
    quote = QuoteEnum.EUR
    crypto = CryptoEnum.DASH


class KrakenTradesEOSEURInput(ABCKrakenTradesInput):
    """Kraken trade input for OSE crypto vs R quote"""
    pair = "EOSEUR"
    quote = QuoteEnum.EUR
    crypto = CryptoEnum.EOS


class KrakenTradesGNOEURInput(ABCKrakenTradesInput):
    """Kraken trade input for NOE crypto vs R quote"""
    pair = "GNOEUR"
    quote = QuoteEnum.EUR
    crypto = CryptoEnum.GNO


class KrakenTradesXETCZEURInput(ABCKrakenTradesInput):
    """Kraken trade input for ETC crypto vs EUR quote"""
    pair = "XETCZEUR"
    quote = QuoteEnum.EUR
    crypto = CryptoEnum.ETC


class KrakenTradesXETHZEURInput(ABCKrakenTradesInput):
    """Kraken trade input for ETH crypto vs EUR quote"""
    pair = "XETHZEUR"
    quote = QuoteEnum.EUR
    crypto = CryptoEnum.ETH


class KrakenTradesXLTCZEURInput(ABCKrakenTradesInput):
    """Kraken trade input for LTC crypto vs EUR quote"""
    pair = "XLTCZEUR"
    quote = QuoteEnum.EUR
    crypto = CryptoEnum.LTC


class KrakenTradesXREPZEURInput(ABCKrakenTradesInput):
    """Kraken trade input for REP crypto vs EUR quote"""
    pair = "XREPZEUR"
    quote = QuoteEnum.EUR
    crypto = CryptoEnum.REP


class KrakenTradesXXBTZEURInput(ABCKrakenTradesInput):
    """Kraken trade input for XBT crypto vs EUR quote"""
    pair = "XXBTZEUR"
    quote = QuoteEnum.EUR
    crypto = CryptoEnum.XBT


class KrakenTradesXXLMZEURInput(ABCKrakenTradesInput):
    """Kraken trade input for XLM crypto vs EUR quote"""
    pair = "XXLMZEUR"
    quote = QuoteEnum.EUR
    crypto = CryptoEnum.XLM


class KrakenTradesXXMRZEURInput(ABCKrakenTradesInput):
    """Kraken trade input for XMR crypto vs EUR quote"""
    pair = "XXMRZEUR"
    quote = QuoteEnum.EUR
    crypto = CryptoEnum.XMR


class KrakenTradesXXRPZEURInput(ABCKrakenTradesInput):
    """Kraken trade input for XRP crypto vs EUR quote"""
    pair = "XXRPZEUR"
    quote = QuoteEnum.EUR
    crypto = CryptoEnum.XRP


class KrakenTradesXZECZEURInput(ABCKrakenTradesInput):
    """Kraken trade input for ZEC crypto vs EUR quote"""
    pair = "XZECZEUR"
    quote = QuoteEnum.EUR
    crypto = CryptoEnum.ZEC


# ###################################### GBP ################################# #

class KrakenTradesXETCZGBPInput(ABCKrakenTradesInput):
    """Kraken trade input for ETC crypto vs GBP quote"""
    pair = "XETCZGBP"
    quote = QuoteEnum.GBP
    crypto = CryptoEnum.ETC


class KrakenTradesXETHZGBPInput(ABCKrakenTradesInput):
    """Kraken trade input for ETH crypto vs GBP quote"""
    pair = "XETHZGBP"
    quote = QuoteEnum.GBP
    crypto = CryptoEnum.ETH


class KrakenTradesXLTCZGBPInput(ABCKrakenTradesInput):
    """Kraken trade input for LTC crypto vs GBP quote"""
    pair = "XLTCZGBP"
    quote = QuoteEnum.GBP
    crypto = CryptoEnum.LTC


class KrakenTradesXREPZGBPInput(ABCKrakenTradesInput):
    """Kraken trade input for REP crypto vs GBP quote"""
    pair = "XREPZGBP"
    quote = QuoteEnum.GBP
    crypto = CryptoEnum.REP


class KrakenTradesXXBTZGBPInput(ABCKrakenTradesInput):
    """Kraken trade input for XBT crypto vs GBP quote"""
    pair = "XXBTZGBP"
    quote = QuoteEnum.GBP
    crypto = CryptoEnum.XBT


class KrakenTradesXXLMZGBPInput(ABCKrakenTradesInput):
    """Kraken trade input for XLM crypto vs GBP quote"""
    pair = "XXLMZGBP"
    quote = QuoteEnum.GBP
    crypto = CryptoEnum.XLM


class KrakenTradesXXMRZGBPInput(ABCKrakenTradesInput):
    """Kraken trade input for XMR crypto vs GBP quote"""
    pair = "XXMRZGBP"
    quote = QuoteEnum.GBP
    crypto = CryptoEnum.XMR


class KrakenTradesXXRPZGBPInput(ABCKrakenTradesInput):
    """Kraken trade input for XRP crypto vs GBP quote"""
    pair = "XXRPZGBP"
    quote = QuoteEnum.GBP
    crypto = CryptoEnum.XRP


class KrakenTradesXZECZGBPInput(ABCKrakenTradesInput):
    """Kraken trade input for ZEC crypto vs GBP quote"""
    pair = "XZECZGBP"
    quote = QuoteEnum.GBP
    crypto = CryptoEnum.ZEC


# ###################################### JPY ################################# #

class KrakenTradesXETCZJPYInput(ABCKrakenTradesInput):
    """Kraken trade input for ETC crypto vs JPY quote"""
    pair = "XETCZJPY"
    quote = QuoteEnum.JPY
    crypto = CryptoEnum.ETC


class KrakenTradesXETHZJPYInput(ABCKrakenTradesInput):
    """Kraken trade input for ETH crypto vs JPY quote"""
    pair = "XETHZJPY"
    quote = QuoteEnum.JPY
    crypto = CryptoEnum.ETH


class KrakenTradesXLTCZJPYInput(ABCKrakenTradesInput):
    """Kraken trade input for LTC crypto vs JPY quote"""
    pair = "XLTCZJPY"
    quote = QuoteEnum.JPY
    crypto = CryptoEnum.LTC


class KrakenTradesXREPZJPYInput(ABCKrakenTradesInput):
    """Kraken trade input for REP crypto vs JPY quote"""
    pair = "XREPZJPY"
    quote = QuoteEnum.JPY
    crypto = CryptoEnum.REP


class KrakenTradesXXBTZJPYInput(ABCKrakenTradesInput):
    """Kraken trade input for XBT crypto vs JPY quote"""
    pair = "XXBTZJPY"
    quote = QuoteEnum.JPY
    crypto = CryptoEnum.XBT


class KrakenTradesXXLMZJPYInput(ABCKrakenTradesInput):
    """Kraken trade input for XLM crypto vs JPY quote"""
    pair = "XXLMZJPY"
    quote = QuoteEnum.JPY
    crypto = CryptoEnum.XLM


class KrakenTradesXXMRZJPYInput(ABCKrakenTradesInput):
    """Kraken trade input for XMR crypto vs JPY quote"""
    pair = "XXMRZJPY"
    quote = QuoteEnum.JPY
    crypto = CryptoEnum.XMR


class KrakenTradesXXRPZJPYInput(ABCKrakenTradesInput):
    """Kraken trade input for XRP crypto vs JPY quote"""
    pair = "XXRPZJPY"
    quote = QuoteEnum.JPY
    crypto = CryptoEnum.XRP


class KrakenTradesXZECZJPYInput(ABCKrakenTradesInput):
    """Kraken trade input for ZEC crypto vs JPY quote"""
    pair = "XZECZJPY"
    quote = QuoteEnum.JPY
    crypto = CryptoEnum.ZEC


# ###################################### USD ################################# #

class KrakenTradesBCHUSDInput(ABCKrakenTradesInput):
    """Kraken trade input for CHU crypto vs D quote"""
    pair = "BCHUSD"
    quote = QuoteEnum.USD
    crypto = CryptoEnum.BCH


class KrakenTradesDASHUSDInput(ABCKrakenTradesInput):
    """Kraken trade input for ASH crypto vs SD quote"""
    pair = "DASHUSD"
    quote = QuoteEnum.USD
    crypto = CryptoEnum.DASH


class KrakenTradesEOSUSDInput(ABCKrakenTradesInput):
    """Kraken trade input for OSU crypto vs D quote"""
    pair = "EOSUSD"
    quote = QuoteEnum.USD
    crypto = CryptoEnum.EOS


class KrakenTradesGNOUSDInput(ABCKrakenTradesInput):
    """Kraken trade input for NOU crypto vs D quote"""
    pair = "GNOUSD"
    quote = QuoteEnum.USD
    crypto = CryptoEnum.GNO


class KrakenTradesXETCZUSDInput(ABCKrakenTradesInput):
    """Kraken trade input for ETC crypto vs USD quote"""
    pair = "XETCZUSD"
    quote = QuoteEnum.USD
    crypto = CryptoEnum.ETC


class KrakenTradesXETHZUSDInput(ABCKrakenTradesInput):
    """Kraken trade input for ETH crypto vs USD quote"""
    pair = "XETHZUSD"
    quote = QuoteEnum.USD
    crypto = CryptoEnum.ETH


class KrakenTradesXLTCZUSDInput(ABCKrakenTradesInput):
    """Kraken trade input for LTC crypto vs USD quote"""
    pair = "XLTCZUSD"
    quote = QuoteEnum.USD
    crypto = CryptoEnum.LTC


class KrakenTradesXREPZUSDInput(ABCKrakenTradesInput):
    """Kraken trade input for REP crypto vs USD quote"""
    pair = "XREPZUSD"
    quote = QuoteEnum.USD
    crypto = CryptoEnum.REP


class KrakenTradesXXBTZUSDInput(ABCKrakenTradesInput):
    """Kraken trade input for XBT crypto vs USD quote"""
    pair = "XXBTZUSD"
    quote = QuoteEnum.USD
    crypto = CryptoEnum.XBT


class KrakenTradesXXLMZUSDInput(ABCKrakenTradesInput):
    """Kraken trade input for XLM crypto vs USD quote"""
    pair = "XXLMZUSD"
    quote = QuoteEnum.USD
    crypto = CryptoEnum.XLM


class KrakenTradesXXMRZUSDInput(ABCKrakenTradesInput):
    """Kraken trade input for XMR crypto vs USD quote"""
    pair = "XXMRZUSD"
    quote = QuoteEnum.USD
    crypto = CryptoEnum.XMR


class KrakenTradesXXRPZUSDInput(ABCKrakenTradesInput):
    """Kraken trade input for XRP crypto vs USD quote"""
    pair = "XXRPZUSD"
    quote = QuoteEnum.USD
    crypto = CryptoEnum.XRP


class KrakenTradesXZECZUSDInput(ABCKrakenTradesInput):
    """Kraken trade input for ZEC crypto vs USD quote"""
    pair = "XZECZUSD"
    quote = QuoteEnum.USD
    crypto = CryptoEnum.ZEC
