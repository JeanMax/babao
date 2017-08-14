"""Here we take the raw trade data and resample it
based on the time interval given in the config file"""

import os
import pandas as pd

import babao.config as conf
import babao.utils.log as log
import babao.utils.fileutils as fu


def _doResample(raw_data, time_interval):
    """
    Resample ´raw_data´ based on ´time_interval´

    Return a DataFrame with these columns:
    index=time, "open", "high", "low", "close", "vwap", "volume", "count"
    """

    # datetime needed for .resample()
    raw_data.index = pd.to_datetime(raw_data.index, unit="us")

    # resample data: it's actually faster to do these one by one
    resampled_data = raw_data["price"].resample(time_interval).ohlc()

    # tmp var for ordering
    v = raw_data["volume"].resample(time_interval).sum()
    resampled_data["vwap"] = raw_data["vwap"].resample(time_interval).sum() / v
    resampled_data["volume"] = v
    resampled_data["count"] = raw_data["price"].resample(time_interval).count()

    # back to unix timestamp (// pd.Timedelta(1, unit="us"))
    resampled_data.index = resampled_data.index.view("int64") // 1000

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


def _getPreviousResampledLine(resampled_data):
    """
    Search for line preceding ´resampled_data´ in conf.RESAMPLED_TRADES_FILE
    """

    # TODO: add a real method for that in fileutils
    prev = fu.getLastLines(
        conf.RESAMPLED_TRADES_FILE,
        42,
        conf.RESAMPLED_TRADES_COLUMNS
    )
    prev.index = pd.to_datetime(prev.index, unit="us")
    try:
        return prev.loc[
            resampled_data.index[0]
            - (resampled_data.index[1] - resampled_data.index[0])
        ]
    except KeyError:
        log.warning("_getPreviousResampledLine() couldn't find anything")
        return None


def _getUnsampled(raw_data, resampled_data):
    """Return raw data used to calculate last candle"""

    # "before" is a concept
    unsampled_data = raw_data.truncate(
        before=pd.to_datetime(resampled_data[-1:].index[0], unit="us")
    )

    # back to unix timestamp (// pd.Timedelta(1, unit="us"))
    unsampled_data.index = unsampled_data.index.view("int64") // 1000

    return unsampled_data


# TODO: test empty raw_data
def resampleTradeData(raw_data):
    """
    Resample ´raw_data´ based on ´conf.TIME_INTERVAL´

    ´raw_data´ is just the last fecthed data, not the whole file

    Return a DataFrame with these columns:
    index=time, "open", "high", "low", "close", "vwap", "volume", "count"
    """

    # previous raw data used to calculate last candle
    if os.path.isfile(conf.UNSAMPLED_TRADES_FILE):
        unsampled_data = fu.readFile(
            conf.UNSAMPLED_TRADES_FILE,
            names=conf.RAW_TRADES_COLUMNS
        )
        raw_data = pd.concat([unsampled_data, raw_data])

    resampled_data = _doResample(raw_data, str(conf.TIME_INTERVAL) + "Min")

    # ffill() need a previous value...
    if resampled_data["vwap"].isnull().iloc[0]:
        resampled_data = _fillMissing(
            resampled_data,
            prev_line=_getPreviousResampledLine(resampled_data)
        )
    else:
        resampled_data = _fillMissing(resampled_data)

    unsampled_data = _getUnsampled(raw_data, resampled_data)

    fu.writeFile(conf.UNSAMPLED_TRADES_FILE, unsampled_data)
    fu.removeLastLine(conf.RESAMPLED_TRADES_FILE, int(resampled_data.index[0]))
    fu.writeFile(conf.RESAMPLED_TRADES_FILE, resampled_data, mode="a")

    return len(resampled_data)
