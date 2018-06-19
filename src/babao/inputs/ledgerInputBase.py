"""
TODO
Handle money related stuffs
"""

import pandas as pd
from abc import abstractmethod

from babao.inputs.inputBase import ABCInput


class ABCLedgerInput(ABCInput):
    """TODO"""

    raw_columns = [
        "type", "volume", "balance", "product"
    ]
    resampled_columns = [
        "balance"
    ]

    def __init__(self):
        super().__init__()
        self.verbose = True

    def _resample(self, raw_data):
        """TODO"""
        resampled_data = self._resampleSerie(raw_data["balance"]).last()
        return pd.DataFrame(
            resampled_data,
            columns=self.__class__.resampled_columns
        )

    def _fillMissing(self, resampled_data):
        """TODO"""
        resampled_data["balance"].ffill(inplace=True)
        resampled_data["balance"].fillna(0, inplace=True)
        return resampled_data

    @abstractmethod
    def buy(self, ledger, volume):
        pass

    @abstractmethod
    def sell(self, ledger, volume):
        pass

    @abstractmethod
    def deposit(self, volume):
        pass

    @abstractmethod
    def withdraw(self, volume):
        pass
