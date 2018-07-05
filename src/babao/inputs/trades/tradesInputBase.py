"""
TODO
"""

from abc import abstractmethod
import numpy as np

import babao.inputs.inputBase as ib


class ABCTradesInput(ib.ABCInput):
    """Base class for any kraken trades input"""

    raw_columns = [
        "price", "volume"
    ]
    resampled_columns = [
        "open", "high", "low", "close", "vwap", "volume", "count"
    ]

    @property
    @abstractmethod
    def quote(self):
        """
        Overide this method with the desired QuoteEnum
        ex: self.quote = QuoteEnum.EUR
        """
        pass

    @property
    @abstractmethod
    def crypto(self):
        """
        Overide this method with the desired CryptoEnum
        ex: self.crypto = CryptoEnum.XBT
        """
        pass

    def _resample(self, raw_data):
        """TODO"""
        p = ib.resampleSerie(raw_data["price"])
        resampled_data = p.ohlc()

        # tmp var for ordering
        v = ib.resampleSerie(raw_data["volume"]).sum()
        resampled_data["vwap"] = ib.resampleSerie(
            raw_data["price"] * raw_data["volume"]
        ).sum() / v
        resampled_data["volume"] = v
        resampled_data["count"] = p.count()

        return resampled_data

    def fillMissing(self, resampled_data):
        """Fill missing values in ´resampled_data´"""
        resampled_data["volume"].fillna(0, inplace=True)
        resampled_data["vwap"].replace(np.inf, np.nan, inplace=True)

        i = resampled_data.index[0]
        for col in ["vwap", "close"]:
            if np.isnan(resampled_data.loc[i, col]):
                if self.last_row is not None:
                    resampled_data.loc[i, col] = self.last_row[col]
                else:
                    resampled_data.loc[i, col] = 0
            resampled_data[col].ffill(inplace=True)

        c = resampled_data["close"]
        resampled_data["open"].fillna(c, inplace=True)
        resampled_data["high"].fillna(c, inplace=True)
        resampled_data["low"].fillna(c, inplace=True)

        return resampled_data

    @abstractmethod
    def fetch(self):
        pass
