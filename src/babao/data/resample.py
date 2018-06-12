"""
Here we take the raw trade data and resample it
based on the time interval given in the config file
"""

import babao.utils.date as du
import babao.config as conf


def _doResample(raw_data, time_interval):
    """
    Resample ´raw_data´ based on ´time_interval´

    Return a DataFrame with these columns:
    index=time, "open", "high", "low", "close", "vwap", "volume", "count"
    """

    # datetime needed for .resample()

    du.to_datetime(raw_data)

    base = raw_data.index[-1]
    base = (base.minute + (base.second + 1) / 60) % 60

    def _resample_wrapper(s):
        """Call Serie.resample on s with preset parameters"""

        return s.resample(
            time_interval,
            closed="right",
            label="right",
            base=base
        )

    p = _resample_wrapper(raw_data["price"])
    resampled_data = p.ohlc()

    # tmp var for ordering
    v = _resample_wrapper(raw_data["volume"]).sum()
    resampled_data["vwap"] = _resample_wrapper(
        raw_data["price"] * raw_data["volume"]
    ).sum() / v
    resampled_data["volume"] = v
    resampled_data["count"] = p.count()

    du.to_timestamp(resampled_data)

    return resampled_data


def _fillMissing(resampled_data, prev_line=None):
    """Fill missing values in ´resampled_data´"""

    resampled_data["volume"] = resampled_data["volume"].fillna(0)

    # TODO: inplace=True
    if prev_line is not None:
        i = resampled_data.index[0]
        resampled_data.loc[i, "vwap"] = prev_line["vwap"]
        resampled_data.loc[i, "close"] = prev_line["close"]

    resampled_data["vwap"] = resampled_data["vwap"].ffill()
    resampled_data["close"] = resampled_data["close"].ffill()

    c = resampled_data["close"]
    resampled_data["open"] = resampled_data["open"].fillna(c)
    resampled_data["high"] = resampled_data["high"].fillna(c)
    resampled_data["low"] = resampled_data["low"].fillna(c)

    return resampled_data


# TODO: test empty raw_data
def resampleTradeData(raw_data):
    """
    Resample ´raw_data´ based on ´conf.TIME_INTERVAL´

    ´raw_data´ is just the last fecthed data, not the whole file

    Return a DataFrame with these columns:
    index=time, "open", "high", "low", "close", "vwap", "volume", "count"
    """

    resampled_data = _doResample(raw_data, str(conf.TIME_INTERVAL) + "Min")

    # ffill() need a previous value...
    # if resampled_data["vwap"].isnull().iloc[0]:  # TODO
    resampled_data = _fillMissing(resampled_data)

    return resampled_data
