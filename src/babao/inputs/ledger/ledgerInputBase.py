"""
TODO
Handle money related stuffs

TODO:
It is really not obvious how you're gonna link the transaction across
various ledgers... kraken doesn't give you anything else than an "order id",
so you still have to iterate over all entries in all ledgers to find the
matching one :/
The good new is, I don't know when we'll need that!
Anyway, I'll leave an empty column "product", which reference another ledger;
this could be used for later indexing?
"""

from abc import abstractmethod
from typing import Union

import pandas as pd

from babao.inputs.inputBase import ABCInput, resampleSerie
from babao.utils.enum import CryptoEnum, QuoteEnum


class ABCLedgerInput(ABCInput):
    """TODO"""

    raw_columns = [
        "volume", "balance", "fee", "refid", "type", "product"
    ]
    resampled_columns = [
        "balance"
    ]

    @property
    @abstractmethod
    def asset(self) -> Union[CryptoEnum, QuoteEnum]:
        """TODO"""
        pass

    def __init__(self):
        ABCInput.__init__(self)
        self.verbose = True

    def _resample(self, raw_data):
        """TODO"""
        resampled_data = resampleSerie(raw_data["balance"]).last()
        return pd.DataFrame(
            resampled_data,
            columns=self.__class__.resampled_columns
        )

    def fillMissing(self, resampled_data):
        """TODO"""
        resampled_data["balance"].ffill(inplace=True)
        resampled_data["balance"].fillna(0, inplace=True)
        return resampled_data

    @abstractmethod
    def buy(self, ledger, volume_spent, price, timestamp=None):
        """TODO"""
        pass

    @abstractmethod
    def sell(self, ledger, volume_spent, price, timestamp=None):
        """TODO"""
        pass

    @abstractmethod
    def deposit(self, ledger, volume, timestamp=None):
        """TODO"""
        pass

    @abstractmethod
    def withdraw(self, ledger, volume, timestamp=None):
        """TODO"""
        pass
