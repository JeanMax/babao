"""
TODO
"""

from abc import abstractmethod

import numpy as np
import pandas as pd

import babao.utils.date as du
from babao.inputs.krakenInputBase import ABCKrakenInput
from babao.inputs.trades.tradesInputBase import ABCTradesInput


class ABCKrakenTradesInput(ABCTradesInput, ABCKrakenInput):
    """Base class for any kraken trades input"""

    @property
    @abstractmethod
    def pair(self):
        """
        Overide this method with the desired asset pair as string
        ex: self.pair = "XXBTZEUR"
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
        if res is None:
            self.up_to_date = False
            return None

        fresh_data = pd.DataFrame(
            res[self.__class__.pair],
            columns=[  # as returned by kraken api
                "price", "volume", "time", "buy-sell", "market-limit", "misc"
            ],
            dtype=float
        )

        if not fresh_data.empty:
            fresh_data.index = np.append(
                du.secToNano(fresh_data["time"].iloc[:-1]),
                int(res["last"])
            )

        self.up_to_date = len(fresh_data) != 1000

        del fresh_data["misc"]
        del fresh_data["market-limit"]  # TODO: this could be useful
        del fresh_data["buy-sell"]  # TODO: this could be useful
        del fresh_data["time"]

        return fresh_data
