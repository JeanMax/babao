"""
Handle logging in database all our transactions

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
    """Base class for any ledger"""

    raw_columns = [
        "volume", "balance", "fee", "refid", "type", "product"
    ]
    resampled_columns = [
        "balance"
    ]

    @property
    @abstractmethod
    def asset(self) -> Union[CryptoEnum, QuoteEnum]:
        """
        Overide this method with the desired CryptoEnum / QuoteEnum
        ex: self.asset = CryptoEnum.XBT
        """
        pass

    def __init__(self):
        ABCInput.__init__(self)
        self.verbose = True

    def _resample(self, raw_data):
        resampled_data = resampleSerie(raw_data["balance"]).last()
        return pd.DataFrame(
            resampled_data,
            columns=self.__class__.resampled_columns
        )

    def fillMissing(self, resampled_data):
        resampled_data["balance"].ffill(inplace=True)
        resampled_data["balance"].fillna(0, inplace=True)
        return resampled_data

    @abstractmethod
    def buy(self, ledger, volume_spent, price, timestamp=None):
        """
        Buy with the current ledger asset the asset of the given ´ledger´

        (If the current ledger is a quote, this is a buy)
         ´volume_spent´ quantity spent (including fees)
        """
        pass

    @abstractmethod
    def sell(self, ledger, volume_spent, price, timestamp=None):
        """
        Buy with the asset of the given ´ledger´ the current ledger asset

        (If the current ledger is a quote, this is a sell)
         ´volume_spent´ quantity spent (including fees)
        """
        pass

    @abstractmethod
    def deposit(self, ledger, volume, timestamp=None):
        """Deposit from the current ledger to the given ´ledger´"""
        pass

    @abstractmethod
    def withdraw(self, ledger, volume, timestamp=None):
        """Withdraw from the current ledger to the given ´ledger´"""
        pass
