"""Buy/Sell strategy"""

import babao.utils.log as log
import babao.strategy.ledger as ledger


def analyse(indicators_data):
    """Just a dummy strategy"""

    log.debug("Entering analyse()")

    current_price = float(indicators_data.tail(1)["close"])

    if ledger.BALANCE["XXBT"] > 0.001:
        if current_price > ledger.minSellPrice():
            ledger.logTransaction(
                "sell",
                current_price,
                ledger.BALANCE["XXBT"]
            )
    else:
        if current_price < ledger.maxBuyPrice():
            ledger.logTransaction(
                "buy",
                current_price,
                ledger.BALANCE["ZEUR"] / current_price
            )
