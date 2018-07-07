"""
TODO
Handle money related stuffs
"""

import sys
from abc import abstractmethod

import pandas as pd

import babao.utils.date as du
import babao.utils.log as log
from babao.inputs.ledger.ledgerInputBase import ABCLedgerInput
from babao.utils.enum import CryptoEnum, QuoteEnum, ActionEnum


class ABCFakeLedgerInput(ABCLedgerInput):
    """TODO"""

    @property
    @abstractmethod
    def asset(self):
        """TODO"""
        pass

    def __init__(self, log_to_file=True):
        ABCLedgerInput.__init__(self)
        self.log_to_file = log_to_file
        if self.last_row is not None and log_to_file:
            self.balance = self.last_row["balance"]
            self.last_tx = self.last_row.name
        else:
            self.balance = 0
            self.last_tx = 0

    def fetch(self):
        pass  # we said fake

    def logTransaction(
            self, typ, volume, refid,
            fee=0, product=0, timestamp=None
    ):
        """
        TODO
        Log transaction in a csv ledger file

        ´led_dic´ is a dict with keys == conf.RAW_LEDGER_COLUMNS
        if ´timestamp´ is not given, the current time will be used
        """

        if timestamp is None:
            timestamp = du.nowMinus(0)

        self.balance += volume - fee
        self.last_tx = timestamp

        if not self.log_to_file:
            return

        df = pd.DataFrame(
            {
                "volume": volume,
                "balance": self.balance,
                "fee": fee,
                "refid": refid,
                "type": typ,
                "product": product,
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
        refid = str(du.nowMinus(0))
        if self.verbose:
            log.info(
                "Bought", round(volume_bought - fee, 4), ledger.asset.name,
                "for", round(volume_spent, 4), self.asset.name,
                "@", int(price)
            )

        self.logTransaction(
            typ=ActionEnum.SELL.value,
            volume=-volume_spent,
            refid=refid,
            product=ledger.asset.value,
            timestamp=timestamp
        )
        ledger.logTransaction(
            typ=ActionEnum.BUY.value,
            volume=volume_bought,
            refid=refid,
            fee=fee,
            product=self.asset.value,
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
        refid = str(du.nowMinus(0))
        if self.verbose:
            log.info(
                "Sold", round(volume_spent, 4), ledger.asset.name,
                "for", round(volume_bought - fee, 4), self.asset.name,
                "@", int(price)
            )

        ledger.logTransaction(
            typ=ActionEnum.SELL.value,
            volume=-volume_spent,
            refid=refid,
            product=self.asset.value,
            timestamp=timestamp
        )
        self.logTransaction(
            typ=ActionEnum.BUY.value,
            volume=volume_bought,
            refid=refid,
            fee=fee,
            product=ledger.asset.value,
            timestamp=timestamp
        )
        return True

    def deposit(self, ledger, volume, timestamp=None):
        """TODO"""
        fee = volume / 100  # 1% hardcoded fee
        refid = str(du.nowMinus(0))
        if self.verbose:
            log.info(
                "Deposit ", round(volume, 4),
                "from", ledger.asset.name,
                "to", self.asset.name,
            )
        self.logTransaction(
            typ=ActionEnum.WITHDRAW.value,
            volume=volume,
            refid=refid,
            product=ledger.asset.value,
            timestamp=timestamp
        )
        ledger.logTransaction(
            typ=ActionEnum.DEPOSIT.value,
            volume=volume,
            refid=refid,
            fee=fee,
            product=self.asset.value,
            timestamp=timestamp
        )

    def withdraw(self, ledger, volume, timestamp=None):
        """TODO"""
        fee = volume / 100  # 1% hardcoded fee
        refid = str(du.nowMinus(0))
        if self.verbose:
            log.info(
                "Withdraw ", round(volume, 4),
                "from", ledger.asset.name,
                "to", self.asset.name,
            )
        ledger.logTransaction(
            typ=ActionEnum.WITHDRAW.value,
            volume=volume,
            refid=refid,
            product=self.asset.value,
            timestamp=timestamp
        )
        self.logTransaction(
            typ=ActionEnum.DEPOSIT.value,
            volume=volume,
            refid=refid,
            fee=fee,
            product=ledger.asset.value,
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
