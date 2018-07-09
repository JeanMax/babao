"""
TODO
"""

from abc import abstractmethod

import pandas as pd

import babao.utils.log as log
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
        if self.current_row is None:
            since = 0  # TODO: do we really need allllll the data? du.EPOCH
        else:
            since = self.current_row.name

        res = self._doRequest("Trades", {
            "pair": self.__class__.pair,
            "since": str(since)
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
            fresh_data["time"] = du.secToNano(fresh_data["time"])

            if not fresh_data["time"].is_monotonic_increasing:
                log.warning("Sorting kraken data -.-")
                fresh_data.sort_values(by=['time'], inplace=True)

            fresh_data.loc[
                fresh_data["time"] == fresh_data["time"].iat[-1],
                "time"
            ] = int(res["last"])

            if since > fresh_data["time"].iat[0]:
                fresh_data.loc[
                    fresh_data["time"] < since,
                    "time"
                ] = since

            fresh_data.index = fresh_data["time"]

        del fresh_data["misc"]
        del fresh_data["market-limit"]  # TODO: this could be useful
        del fresh_data["buy-sell"]  # TODO: this could be useful
        del fresh_data["time"]

        self.up_to_date = len(fresh_data) != 1000
        return fresh_data
