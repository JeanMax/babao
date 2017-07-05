"""TODO"""

import os
import pandas as pd

import babao.log as log
import babao.config as conf
import babao.fileutils as fu


def resampleData(raw_data):
    """´raw_data´ is just the last fecthed data, not the whole file
       WARNING: an interval with 0 transaction will output a line like this:
       TIMESTAMP,,,,,,,0
    """
    log.debug("Entering resampleData()")

    # previous raw data used to calculate last candle
    if os.path.isfile(conf.UNSAMPLED_FILE):
        unsampled_data = fu.readFile(
            conf.UNSAMPLED_FILE,
            names=["price", "volume", "buy-sell", "market-limit", "vwap"]
        )
        raw_data = pd.concat([unsampled_data, raw_data])

    raw_data.index = pd.to_datetime(raw_data.index, unit="s")

    time_interval = str(conf.TIME_INTERVAL) + "Min"
    # resample data: it's actually faster to do these one by one
    # see on top of file for divide by 0 handling
    resampled_data = raw_data["price"].resample(time_interval).ohlc()

    # tmp var for ordering
    v = raw_data["volume"].resample(time_interval).sum()
    resampled_data["vwap"] = raw_data["vwap"].resample(time_interval).sum() / v
    resampled_data["volume"] = v
    resampled_data["count"] = raw_data["price"].resample(time_interval).count()

    # TODO: I highly (yep) doubt this is necessary
    resampled_data.index = resampled_data.index.view("int64") \
        // pd.Timedelta(1, unit="s")

    # save raw data used to calculate last candle ("before" is a concept)
    unsampled_data = raw_data.truncate(
        before=pd.to_datetime(resampled_data[-1:].index[0], unit="s")
    )

    # TODO: idem
    unsampled_data.index = unsampled_data.index.view("int64") \
        // pd.Timedelta(1, unit="s")
    fu.writeFile(conf.UNSAMPLED_FILE, unsampled_data)

    fu.removeLastLine(conf.RESAMPLED_FILE, resampled_data.index[0])
    fu.writeFile(conf.RESAMPLED_FILE, resampled_data, mode="a")

    return len(resampled_data)
