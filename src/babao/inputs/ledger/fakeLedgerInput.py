"""
Handle logging in database all our fake transactions (dry-run)
"""

import sys
from abc import abstractmethod

import pandas as pd

import babao.utils.date as du
import babao.utils.log as log
from babao.inputs.ledger.ledgerInputBase import ABCLedgerInput
from babao.utils.enum import CryptoEnum, QuoteEnum, ActionEnum


class ABCFakeLedgerInput(ABCLedgerInput):
    """Base class for any fake ledger"""

    @property
    @abstractmethod
    def asset(self):
        pass

    def __init__(self, log_to_file=True):
        ABCLedgerInput.__init__(self)
        self.log_to_file = log_to_file
        if self.current_row is not None and log_to_file:
            self.balance = self.current_row["balance"]
            self.last_tx = self.current_row.name
        else:
            self.balance = 0
            self.last_tx = 0

    def fetch(self):
        self.up_to_date = True  # we said fake

    def logTransaction(
            self, typ, volume, refid,
            fee=0, product=0, timestamp=None
    ):
        """
        Log transaction in database
        if ´timestamp´ is not given, the current time will be used

        This should'nt be used outside of this class
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
            if c in ["type", "product"]:
                df[c] = df[c].astype(int)
            else:
                df[c] = df[c].astype(float)

        self.write(df)

    def buy(self, ledger, volume_spent, price, timestamp=None):
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
        fee = volume / 100  # 1% hardcoded fee
        refid = str(du.nowMinus(0))
        if self.verbose:
            log.info(
                "Deposit", round(volume, 4),
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
        fee = volume / 100  # 1% hardcoded fee
        refid = str(du.nowMinus(0))
        if self.verbose:
            log.info(
                "Withdraw", round(volume, 4),
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


# Dynamically generate these inkd of classes for all assets available:

# class FakeLedgerEURInput(ABCFakeLedgerInput):
#     asset = QuoteEnum.EUR

for asset in list(QuoteEnum) + list(CryptoEnum):
    cls = "FakeLedger" + asset.name + "Input"
    setattr(
        sys.modules[__name__],
        cls,
        type(cls, (ABCFakeLedgerInput,), {"asset": asset})
    )
