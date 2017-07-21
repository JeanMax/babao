import babao.api.kraken as kraken
from babao.babao import init

# TODO: how should we test private api requests?


def test_getRawTrades():
    init("d")  # TODO: hardcode api config?
    df = kraken.getRawTrades("")
    assert df.index[0] > 1500000000
    assert len(df.index) == 1000
    assert not df["price"].empty
    assert not df["volume"].empty
    assert not df["buy-sell"].empty
    assert not df["market-limit"].empty
    assert not df["vwap"].empty
