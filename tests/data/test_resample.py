# import babao.data.resample as resample
# import babao.api.kraken as kraken
# import babao.config as conf
# import babao.babao as babao


# def test_resampleDate():
#     babao._init("d")  # TODO: hardcode api config?

#     raw_data = kraken.getRawTrades("1380563220")[0]
#     time_interval = str(conf.TIME_INTERVAL) + "Min"
#     resampled_data = resample._doResample(raw_data, time_interval)
#     resampled_data = resample.fillMissing(resampled_data)

#     assert not resampled_data["open"].empty
#     assert not resampled_data["high"].empty
#     assert not resampled_data["low"].empty
#     assert not resampled_data["close"].empty
#     assert not resampled_data["vwap"].empty
#     assert not resampled_data["volume"].empty
#     assert not resampled_data["count"].empty

#     babao._kthxbye()
