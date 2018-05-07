"""
Handle translation between our ledger database format and the ledger-cli format

See https://www.ledger-cli.org/ for more infos about ledger-cli
"""

import pandas as pd


def _printHeader(index, tx_type, currency):
    """Print first line of entry (date/description)"""

    print(
        pd.to_datetime(index // 10**6, unit="s"),
        "*",
        tx_type,
        "(" + currency + ")"
    )


def _printRecipient(rec_name, amount, asset, price=None):
    """Print one line of an entry"""

    left = "\t%s\t\t%f" % (rec_name, amount)
    if price is not None:
        asset = asset + " ; @ " + price  # TODO: price isn't exact
    print(left, asset)


def _printFee(crypto_fee, quote_fee, crypto_name, quote_name):
    """Call _printRecipient on fees if required"""

    if crypto_fee > 0:
        _printRecipient("Expenses:Fee", crypto_fee, crypto_name)
    if quote_fee > 0:
        _printRecipient("Expenses:Fee", quote_fee, quote_name)


def _handleQuoteDeposit(row, crypto_name, quote_name):
    """Do all stuffs needed for deposit (quote)"""

    _printHeader(row.Index, "deposit", quote_name)
    _printRecipient("Assets:Bank\t", row.quote_vol * -1, quote_name)
    _printFee(row.crypto_fee, row.quote_fee, crypto_name, quote_name)
    _printRecipient("Assets:Market", row.quote_vol, quote_name)


def _handleCryptoDeposit(row, crypto_name, quote_name):
    """Do all stuffs needed for deposit (crypto)"""

    _printHeader(row.Index, "deposit", crypto_name)
    _printRecipient("Assets:Bank\t", row.crypto_vol * -1, crypto_name)
    _printFee(row.crypto_fee, row.quote_fee, crypto_name, quote_name)
    _printRecipient("Assets:Market", row.crypto_vol, crypto_name)


def _handleQuoteWithdraw(row, crypto_name, quote_name):
    """Do all stuffs needed for withdraw"""

    _printHeader(row.Index, "withdraw", quote_name)
    _printRecipient("Assets:Market", row.quote_vol * -1, quote_name)
    _printFee(row.crypto_fee, row.quote_fee, crypto_name, quote_name)
    _printRecipient("Assets:Bank\t", row.quote_vol, quote_name)


def _handleCryptoWithdraw(row, crypto_name, quote_name):
    """Do all stuffs needed for withdraw"""

    _printHeader(row.Index, "withdraw", crypto_name)
    _printRecipient("Assets:Market", row.crypto_vol * -1, crypto_name)
    _printFee(row.crypto_fee, row.quote_fee, crypto_name, quote_name)
    _printRecipient("Assets:Bank\t", row.crypto_vol, crypto_name)


def _handleBuy(row, crypto_name, quote_name):
    """Do all stuffs needed for buy"""

    _printHeader(row.Index, "buy", quote_name + " -> " + crypto_name)
    _printRecipient("Assets:Market", row.quote_vol, quote_name)
    _printFee(row.crypto_fee, row.quote_fee, crypto_name, quote_name)
    _printRecipient(
        "Assets:Market",
        row.crypto_vol,
        crypto_name,
        "%f %s" % (row.price, quote_name)
    )


def _handleSell(row, crypto_name, quote_name):
    """Do all stuffs needed for sell"""

    _printHeader(row.Index, "sell", crypto_name + " -> " + quote_name)
    _printRecipient(
        "Assets:Market",
        row.crypto_vol,
        crypto_name,
        "%f %s" % (row.price, quote_name)
    )
    _printFee(row.crypto_fee, row.quote_fee, crypto_name, quote_name)
    _printRecipient("Assets:Market", row.quote_vol, quote_name)


def printCliFormat(ledger_df, crypto_name, quote_name):
    """
    Print the given (raw) ledger DataFrame with ledger-cli format

    ´crypto_name´/´quote_name´ should be strings describing the assets
    exchanged in the ´ledger_df´ (ex: "XXBT"/"ZEUR")

    common usage:
    printCliFormat(
        fu.read(conf.DB_FILE, conf.LEDGER_FRAME),
        conf.ASSET_PAIR[:4],
        conf.ASSET_PAIR[4:]
    )
    """

    for row in ledger_df.itertuples():
        if row.type == "d":
            if row.crypto_vol > 0:
                _handleCryptoDeposit(row, crypto_name, quote_name)
            else:
                _handleQuoteDeposit(row, crypto_name, quote_name)

        elif row.type == "w":  # TODO: check sign
            if row.crypto_vol > 0:
                _handleCryptoWithdraw(row, crypto_name, quote_name)
            else:
                _handleQuoteWithdraw(row, crypto_name, quote_name)

        elif row.type == "b":
            _handleBuy(row, crypto_name, quote_name)

        elif row.type == "s":
            _handleSell(row, crypto_name, quote_name)

        print()
