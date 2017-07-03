"""TODO"""

import os
import mmap
import pandas as pd

import log
import config as conf

# from IPython import embed #; embed() # DEBUG
# import ipdb #; ipdb.set_trace()   # DEBUG

# RAW_FILE is just the last data, not the whole file
def resampleData(raw_data, time_interval):
    """WARNING: an interval with 0 transaction will output a line like this:
       TIMESTAMP,,,,,,,0
    """
    log.debug("Entering resampleData()") # DEBUG

    # current raw data file
    # raw_data = pd.read_csv(
    #     raw_file,
    #     names=["time", "price", "volume"],
    #     engine='c',
    #     parse_dates=True,
    # )


    unsampled_file = os.path.join(
        conf.DATA_DIR,
        conf.ASSET_PAIR + "-unsampled-" + time_interval + ".csv"
    ) #TODO: rename, it's actually resampled
    resampled_file = os.path.join(
        conf.DATA_DIR,
        conf.ASSET_PAIR + "-resampled-" + time_interval + ".csv"
    ) #TODO: duplicate

    # previous raw data used to calculate last candle
    if os.path.isfile(unsampled_file):
        unsampled_data = pd.read_csv(
            unsampled_file,
            names=["price", "volume", "buy-sell", "market-limit", "vwap"],
            engine='c',
            parse_dates=True,
        )
        raw_data = pd.concat([unsampled_data, raw_data])


    raw_data.index = pd.to_datetime(raw_data.index, unit="s")

    # resample data: it's actually faster to do these one by one
    # see on top of file for divide by 0 handling
    resampled_data = raw_data["price"].resample(time_interval).ohlc()
    vol = raw_data["volume"].resample(time_interval).sum() #tmp var for ordering
    resampled_data["vwap"] = raw_data["vwap"].resample(time_interval).sum() / vol
    resampled_data["volume"] = vol
    resampled_data["count"] = raw_data["price"].resample(time_interval).count()

    resampled_data.index = resampled_data.index.view("int64") // pd.Timedelta(1, unit="s")

    # save raw data used to calculate last candle
    unsampled_data = raw_data.truncate(
        before=pd.to_datetime(resampled_data[-1:].index[0], unit="s")
    )
    unsampled_data.index = unsampled_data.index.view("int64") // pd.Timedelta(1, unit="s")
    unsampled_data.to_csv(unsampled_file, header=False)


    # remove last entry in resampled_file
    # if it match first timestamp of resampled_data
    # TODO: this would need an update if changing for hdf data files
    if os.path.isfile(resampled_file):
        with open(resampled_file, 'r+b') as resampled, mmap.mmap(resampled.fileno(), 0, access=mmap.ACCESS_WRITE) as mm:
            last_line_pos = mm.rfind(b'\n', 0, len(mm) - 1) + 1
            if resampled_data.index[0] == int(mm[last_line_pos:last_line_pos + 10]): #timestamps are formated to 10 digits
                mm.resize(last_line_pos)

    resampled_data.to_csv(resampled_file, header=False, mode="a")
