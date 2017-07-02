#!/usr/bin/env python


import os #path.isfile
import sys #argv
import mmap
import pandas as pd #that part take a while ><

# RAW_FILE is just the last data, not the whole file
def resampleData(raw_file, time_interval, unsampled_file, resampled_file):
    # time,open,high,low,close,vwap,volume,count
    # WARNING: an interval with 0 transaction will output a line like this:
    # TIMESTAMP,,,,,,,0

    # current raw data file
    raw_data = pd.read_csv(
        raw_file,
        names=["time", "price", "volume"],
        engine='c',
        parse_dates=True,
    )

    # previous raw data used to calculate last candle
    if os.path.isfile(unsampled_file):
        unsampled_data = pd.read_csv(
            unsampled_file,
            names=["time", "price", "volume"],
            engine='c',
            parse_dates=True,
        )
        raw_data = pd.concat([unsampled_data, raw_data])

    raw_data.index = pd.to_datetime(raw_data["time"], unit="s")
    raw_data["vwap"] = raw_data["price"] * raw_data["volume"]

    # resample data: it's actually faster to do these one by one (use less memory?)
    # see on top of file for divide by 0 handling
    resampled_data = raw_data["price"].resample(time_interval).ohlc()
    vol = raw_data["volume"].resample(time_interval).sum() #tmp var for ordering
    resampled_data["vwap"] = raw_data["vwap"].resample(time_interval).sum() / vol
    resampled_data["volume"] = vol
    resampled_data["count"] = raw_data["price"].resample(time_interval).count()

    resampled_data.index = resampled_data.index.view("int64") // pd.Timedelta(1, unit="s")

    # save raw data used to calculate last candle
    raw_data.truncate(
        before=pd.to_datetime(resampled_data[-1:].index[0], unit="s")
    ).to_csv(
        unsampled_file, header=False
    )

    # remove last entry in resampled_data.csv
    # if match first timestamp of resampled_data
    # TODO: this would need an update if changing for hdf data files
    if os.path.isfile(resampled_file):
        with open(resampled_file, 'r+b') as resampled, mmap.mmap(resampled.fileno(), 0, access=mmap.ACCESS_WRITE) as mm:
            last_line_pos = mm.rfind(b'\n', 0, len(mm) - 1) + 1
            if resampled_data.index[0] == int(mm[last_line_pos:last_line_pos + 10]): #timestamps are formated to 10 digits
                mm.resize(last_line_pos)

    resampled_data.to_csv(resampled_file, header=False, mode="a")


# https://www.quantinsti.com/blog/build-technical-indicators-in-python
def updateIndicators(resampled_file): #TODO: should handle on the fly flex stuffs man
    # Simple Moving Average
    def indicator_SMA(close_price, look_back_delay): # I think you should differentiate actual parameters from data parameter
        return close_price.rolling(
            window=look_back_delay,
            center=False
        ).mean()

    # Exponentially-weighted Moving Average
    def indicator_EWMA(close_price, look_back_delay):
        return close_price.ewm(
            span=look_back_delay,
            min_periods=look_back_delay - 1,
            adjust=True,
            ignore_na=False
        ).mean()

    #TODO: NaN
    resampled_data = pd.read_csv(
        resampled_file,
        names=["time", "open", "high", "low", "close", "vwap", "volume", "count"],
        engine='c',
        parse_dates=True,
    )
    # resampled_data.index = pd.to_datetime(resampled_data["time"], unit="s")

    # indicators = {
    #     "SMA": indicator_SMA,
    #     "EWMA": indicator_EWMA
    # }
    # indicators_data = {}
    # for indicator_name, indicator_fun in sorted(indicators.items()): #there might be a better way to do that...
    #     indicators_data[indicator_name] = indicator_fun(resampled_data)

    close = resampled_data['close'] #TODO: test if this is really faster
    indicators_data = pd.DataFrame()

    for i in [3, 5, 7]:
        indicators_data["SMA_" + str(i)] = indicator_SMA(close, i)
        indicators_data["EWMA_" + str(i)] = indicator_EWMA(close, i)

    indicators_data.index = resampled_data["time"]
    return indicators_data      # DEBUG



#TODO: bitch about wrong argv usage + some parsing
resampleData(
    sys.argv[1],
    sys.argv[2] + "Min",
    sys.argv[3] + "-unsampled-" + sys.argv[2] + ".csv", #TODO: this is really ugly + rename, it's actually resampled
    sys.argv[3] + "-resampled-" + sys.argv[2] + ".csv" #TODO: this is really ugly
)

updateIndicators(
    sys.argv[3] + "-resampled-" + sys.argv[2] + ".csv" #TODO: this is really ugly + redudant
)
