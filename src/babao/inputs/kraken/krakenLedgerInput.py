"""
TODO
Handle money related stuffs
"""

import sys
import pandas as pd
from abc import abstractmethod

import babao.config as conf
from babao.utils.enum import CryptoEnum, QuoteEnum
from babao.inputs.ledgerInputBase import ABCLedgerInput
from babao.inputs.kraken.krakenInputBase import ABCKrakenInput


class ABCKrakenLedgerInput(ABCLedgerInput, ABCKrakenInput):
    """TODO"""

    @abstractmethod
    def asset():
        """TODO"""
        pass

    def __init__(self):
        super().__init__()
        self.balance = {}  # TODO

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
            since = str(self.last_row.name)

        res = self._doRequest("Ledgers", {"start": since})
        # TODO: start param isn't working

        if res["count"] == 0:
            return

        raw_ledger = pd.DataFrame(res["ledger"]).T
        raw_ledger.index = (raw_ledger["time"] * 1e6).astype(int)
        del raw_ledger["time"]
        del raw_ledger["aclass"]
        raw_ledger = raw_ledger.sort_index()

        # raw_ledger = raw_ledger.where(
        #     (raw_ledger["asset"] == conf.ASSET_PAIR[:4])
        #     | (raw_ledger["asset"] == conf.ASSET_PAIR[4:])
        # )

        raw_ledger["amount"] = raw_ledger["amount"].astype(float)
        raw_ledger["fee"] = raw_ledger["fee"].astype(float)
        raw_ledger["balance"] = raw_ledger["balance"].astype(float)

        for i in range(len(raw_ledger)):
            ind = raw_ledger.index[i]

            if raw_ledger.at[ind, "type"] == "deposit":
                if raw_ledger.at[ind, "asset"] == conf.ASSET_PAIR[:4]:
                    ledger.logCryptoDeposit(
                        raw_ledger.at[ind, "amount"],
                        raw_ledger.at[ind, "fee"],
                        ind
                    )
                else:
                    ledger.logQuoteDeposit(
                        raw_ledger.at[ind, "amount"],
                        raw_ledger.at[ind, "fee"],
                        ind
                    )

            elif raw_ledger.at[ind, "type"] == "withdraw":
                # TODO: check if fees should be excluded
                if raw_ledger.at[ind, "asset"] == conf.ASSET_PAIR[:4]:
                    ledger.logCryptoWithdraw(
                        raw_ledger.at[ind, "amount"] * -1,  # TODO: check if < 0
                        raw_ledger.at[ind, "fee"],
                        ind
                    )
                else:
                    ledger.logQuoteWithdraw(
                        raw_ledger.at[ind, "amount"] * -1,  # TODO: check if < 0
                        raw_ledger.at[ind, "fee"],
                        ind
                    )

            elif raw_ledger.at[ind, "type"] == "trade":
                if raw_ledger.at[ind, "asset"] == conf.ASSET_PAIR[:4]:
                    next_ind = raw_ledger.index[i + 1]
                    crypto_vol = abs(raw_ledger.at[ind, "amount"])
                    crypto_fee = raw_ledger.at[ind, "fee"]
                    quote_vol = abs(raw_ledger.at[next_ind, "amount"])
                    quote_fee = raw_ledger.at[next_ind, "fee"]
                    price = quote_vol / crypto_vol
                    if raw_ledger.at[ind, "amount"] > 0:
                        ledger.logBuy(
                            quote_vol + quote_fee,
                            price,
                            crypto_fee,
                            quote_fee,
                            ind
                        )
                    else:
                        ledger.logSell(
                            crypto_vol + crypto_fee,
                            price,
                            crypto_fee,
                            quote_fee,
                            ind
                        )

        return res["count"], str(raw_ledger.index[-1] / 1e6)

    def buy(self, todo):
        pass

    def sell(self, todo):
        pass

    def deposit(self, todo):
        pass

    def withdraw(self, todo):
        pass


# TODO: move that

# class FakeKrakenEURInput(ABCKrakenLedgerInput):
#     asset = QuoteEnum.EUR

for asset in list(QuoteEnum) + list(CryptoEnum):
    cls = "KrakenLedger" + asset.name + "Input"
    setattr(
        sys.modules[__name__],
        cls,
        type(cls, (ABCKrakenLedgerInput,), {"asset": asset})
    )
