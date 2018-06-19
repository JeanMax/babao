"""
TODO
"""

import sys
from abc import abstractmethod
import pandas as pd
import numpy as np

import babao.utils.date as du
from babao.utils.enum import CryptoEnum, QuoteEnum
from babao.inputs.kraken.krakenInputBase import ABCKrakenInput
from babao.inputs.tradesInputBase import ABCTradesInput


class ABCKrakenTradesInput(ABCTradesInput, ABCKrakenInput):
    """Base class for any kraken trades input"""

    @property
    @abstractmethod
    def pair(self):
        """
        Overide this method with the desired asset pair as string
        ex: pair = "XXBTZEUR"
        """
        pass

    def fetch(self):
        """TODO"""
        if self.last_row is None:
            since = "0"  # TODO: do we really need allllll the data?
        else:
            since = str(self.last_row.name)

        res = self._doRequest("Trades", {
            "pair": self.__class__.pair,
            "since": since
        })
        #TODO: handle delay

        fresh_data = pd.DataFrame(
            res[self.__class__.pair],
            columns=[  # as returned by kraken api
                "price", "volume", "time", "buy-sell", "market-limit", "misc"
            ],
            dtype=float  # TODO: dtypes: object(2) (replace letters with int?)
        )

        fresh_data.index = np.append(
            du.secToNano(fresh_data["time"]),
            int(res["last"])
        )
        del fresh_data["misc"]
        del fresh_data["market-limit"]  # TODO: this could be useful
        del fresh_data["buy-sell"]  # TODO: this could be useful
        del fresh_data["time"]

        return fresh_data


# TODO: move that

# class KrakenTradesXXBTZEURInput(ABCKrakenTradesInput):
#     pair = "XXBTZEUR"

for quote in QuoteEnum:
    for crypto in CryptoEnum:
        pair = "X" + crypto.name + "Z" + quote.name
        cls = "KrakenTrades" + pair + "Input"
        setattr(
            sys.modules[__name__],
            cls,
            type(cls, (ABCKrakenTradesInput,), {"pair": pair})
        )
