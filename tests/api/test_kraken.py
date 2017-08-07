import babao.api.kraken as kraken
import babao.babao as babao

# TODO: how should we test private api requests?


def test_getRawTrades():
    babao._init("d")  # TODO: hardcode api config?

    raw_data = kraken.getRawTrades("")[0]

    assert raw_data.index[0] > 1500000000
    assert len(raw_data.index) == 1000
    assert not raw_data["price"].empty
    assert not raw_data["volume"].empty
    assert not raw_data["buy-sell"].empty
    assert not raw_data["market-limit"].empty
    assert not raw_data["vwap"].empty

    babao._kthxbye()
