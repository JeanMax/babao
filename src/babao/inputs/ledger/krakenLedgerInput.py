"""
TODO
Handle money related stuffs
"""

import sys
from abc import abstractmethod
import pandas as pd

import babao.utils.date as du
from babao.utils.enum import CryptoEnum, QuoteEnum, ActionEnum
from babao.inputs.ledger.ledgerInputBase import ABCLedgerInput
from babao.inputs.krakenBase import ABCKrakenInput


class ABCKrakenLedgerInput(ABCLedgerInput, ABCKrakenInput):
    """TODO"""

    @property
    @abstractmethod
    def asset(self):
        """TODO"""
        pass

    def __init__(self):
        super().__init__()
        self.balance = 0  # TODO

    def fetch(self):
        """
        TODO
        Fetch last ledger entries from api

        Transaction will be logged using functions from ledger module
        Return a tuple (numberOfTransactionFetched, str(last_timestamp))
        """

        if self.last_row is None:
            since = "0"
        else:
            since = str(du.nanoToSec(self.last_row.name))

        res = self._doRequest("Ledgers", {
            "start": since, "asset": self.asset.name
        })
        if res["count"] == 0:
            return None

        if res["count"] > 50 and self.last_row is None:
            # kraken api is *STOOPID*: if don't have the exact date of the
            # first transaction, we can't fetch the ledger data starting from
            # the begining... so we'll need a couple extra requests, sorry!
            self._sleep()
            res = self._doRequest("Ledgers", {
                "ofs": res["count"] - 1, "asset": self.asset.name
            })  # first

        raw_ledger = pd.DataFrame(res["ledger"]).T
        if raw_ledger.empty:
            return raw_ledger

        raw_ledger.index = du.secToNano(raw_ledger["time"])
        del raw_ledger["time"]
        del raw_ledger["aclass"]
        del raw_ledger["asset"]
        raw_ledger = raw_ledger.sort_index()
        raw_ledger.rename(columns={"amount": "volume"}, inplace=True)

        raw_ledger["volume"] = raw_ledger["volume"].astype(float)
        raw_ledger["fee"] = raw_ledger["fee"].astype(float)
        raw_ledger["balance"] = raw_ledger["balance"].astype(float)
        raw_ledger["product"] = 0  # TODO: enum?
        raw_ledger.loc[
            (raw_ledger["volume"] > 0) & (raw_ledger["type"] == "trade"), "type"
        ] = "buy"
        raw_ledger["type"] = raw_ledger["type"].replace({
            "withdrawal": ActionEnum.WITHDRAW.value,
            "deposit": ActionEnum.DEPOSIT.value,
            "buy": ActionEnum.BUY.value,
            "trade": ActionEnum.SELL.value,
        }).astype(int)

        return raw_ledger

    def buy(self, ledger, volume_spent, price, timestamp=None):
        raise NotImplementedError("Sorry, this is not implement yet :/")

    def sell(self, ledger, volume_spent, price, timestamp=None):
        raise NotImplementedError("Sorry, this is not implement yet :/")

    def deposit(self, ledger, volume, timestamp=None):
        raise NotImplementedError("Sorry, this is not implement yet :/")

    def withdraw(self, ledger, volume, timestamp=None):
        raise NotImplementedError("Sorry, this is not implement yet :/")


# TODO: move that

# class KrakenLedgerEURInput(ABCKrakenLedgerInput):
#     asset = QuoteEnum.EUR

for asset in list(QuoteEnum) + list(CryptoEnum):
    cls = "KrakenLedger" + asset.name + "Input"
    setattr(
        sys.modules[__name__],
        cls,
        type(cls, (ABCKrakenLedgerInput,), {"asset": asset})
    )
