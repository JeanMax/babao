"""
TODO
Handle money related stuffs
"""

import sys
import time
import pandas as pd
from abc import abstractmethod

import babao.utils.log as log  # TODO: handle mutex
from babao.utils.enum import CryptoEnum, QuoteEnum, ActionEnum
from babao.inputs.ledgerInputBase import ABCLedgerInput


class ABCFakeLedgerInput(ABCLedgerInput):
    """TODO"""

    @abstractmethod
    def asset():
        """TODO"""
        pass

    def __init__(self, log_to_file=True):
        super().__init__()
        self.log_to_file = log_to_file
        if self.last_row is not None:
            self.balance = self.last_row["balance"]
        else:
            self.balance = 0

    def fetch(self):
        pass  # we said fake

    def __logTransaction(self, typ, volume, product=None, timestamp=None):
        """
        TODO
        Log transaction in a csv ledger file

        ´led_dic´ is a dict with keys == conf.RAW_LEDGER_COLUMNS
        if ´timestamp´ is not given, the current time will be used
        """

        self.balance += volume
        if not self.log_to_file:
            return

        if timestamp is None:
            timestamp = int(time.time() * 1e6)
        if product is None:
            product = 0  # TODO: enum?

        df = pd.DataFrame(
            {
                "type": typ,
                "volume": volume,
                "balance": self.balance,
                "product": product
            },
            columns=self.__class__.raw_columns,
            index=[timestamp]
        ).fillna(0)

        for c in df.columns:
            if c == "type" or c == "product":
                df[c] = df[c].astype(int)
            else:
                df[c] = df[c].astype(float)

        self.write(df)

    def buy(self, ledger, volume_spent, price, timestamp=None):
        """
        TODO
        Log a buy transaction (quote -> crypto)

        ´quote_vol´ quantity spent in quote (including fees)
        """

        if self.balance < volume_spent:
            return False

        volume_bought = volume_spent / price
        fee = volume_bought / 100  # 1% hardcoded fee
        if self.verbose:
            log.info(
                "Bought", round(volume_bought - fee, 4), ledger.asset.name,
                "for", round(volume_spent, 4), self.asset.name,
                "@", int(price)
            )

        self.__logTransaction(
            typ=ActionEnum.SELL.value,
            volume=-volume_spent,
            product=ledger.asset.value,
            timestamp=timestamp
        )
        ledger.__logTransaction(
            typ=ActionEnum.BUY.value,
            volume=volume_bought,
            product=self.asset.value,
            timestamp=timestamp
        )
        ledger.__logTransaction(
            typ=ActionEnum.FEE.value,
            volume=-fee,
            timestamp=timestamp
        )
        return True

    def sell(self, ledger, volume_spent, price, timestamp=None):
        """
        TODO
        Log a sell transaction (crypto -> quote)

        ´crypto_vol´ quantity spent in crypto (including fees)
        """

        if ledger.balance < volume_spent:
            return False

        volume_bought = volume_spent * price
        fee = volume_bought / 100  # 1% hardcoded fee
        if self.verbose:
            log.info(
                "Sold", round(volume_spent, 4), ledger.asset.name,
                "for", round(volume_bought - fee, 4), self.asset.name,
                "@", int(price)
            )

        ledger.__logTransaction(
            typ=ActionEnum.SELL.value,
            volume=-volume_spent,
            product=self.asset.value,
            timestamp=timestamp
        )
        self.__logTransaction(
            typ=ActionEnum.BUY.value,
            volume=volume_bought,
            product=ledger.asset.value,
            timestamp=timestamp
        )
        self.__logTransaction(
            typ=ActionEnum.FEE.value,
            volume=-fee,
            timestamp=timestamp
        )
        return True

    def deposit(self, ledger, volume, timestamp=None):
        """TODO"""
        fee = volume / 100  # 1% hardcoded fee
        self.__logTransaction(
            typ=ActionEnum.WITHDRAW.value,
            volume=volume,
            timestamp=timestamp
        )
        ledger.__logTransaction(
            typ=ActionEnum.DEPOSIT.value,
            volume=volume,
            timestamp=timestamp
        )
        ledger.__logTransaction(
            typ=ActionEnum.FEE.value,
            volume=-fee,
            timestamp=timestamp
        )

    def withdraw(self, ledger, volume, timestamp=None):
        """TODO"""
        fee = volume / 100  # 1% hardcoded fee
        ledger.__logTransaction(
            typ=ActionEnum.WITHDRAW.value,
            volume=volume,
            timestamp=timestamp
        )
        self.__logTransaction(
            typ=ActionEnum.DEPOSIT.value,
            volume=volume,
            timestamp=timestamp
        )
        self.__logTransaction(
            typ=ActionEnum.FEE.value,
            volume=-fee,
            timestamp=timestamp
        )


# TODO: move that

# class FakeLedgerEURInput(ABCFakeLedgerInput):
#     asset = QuoteEnum.EUR

for asset in list(QuoteEnum) + list(CryptoEnum):
    cls = "FakeLedger" + asset.name + "Input"
    setattr(
        sys.modules[__name__],
        cls,
        type(cls, (ABCFakeLedgerInput,), {"asset": asset})
    )
