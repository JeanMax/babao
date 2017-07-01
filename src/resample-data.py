#!/usr/bin/env python

# time,open,high,low,close,vwap,volume,count
# WARNING: an interval with 0 transaction will output a line like this:
# TIMESTAMP,,,,,,,0

import os #path.isfile
import sys #argv
import mmap
import pandas as pd #that part take a while ><

#the file given as parameter is just the last data, not the whole file

#TODO: bitch about wrong argv usage

data_file=sys.argv[1]
time_interval=sys.argv[2] + "Min"
unsampled_file=sys.argv[3] + "-unsampled-" + time_interval + ".csv"
resampled_file=sys.argv[3] + "-resampled-" + time_interval + ".csv" #TODO: this is really ugly


# data_file="~/babao/data/trade-XXBTZEUR.csv"
# time_interval="1Min"
# unsampled_file="/tmp/us.csv"
# resampled_file="/tmp/rs.csv"

# current raw data file
data = pd.read_csv(
    data_file,
    names=["time", "price", "volume"],
    engine='c',
    parse_dates=True,
)

# previous raw data used to calculate last candle
if os.path.isfile(unsampled_file):
    unsampled = pd.read_csv(
        unsampled_file,
        names=["time", "price", "volume"],
        engine='c',
        parse_dates=True,
    )
    data = pd.concat([unsampled, data])

data.index = pd.to_datetime(data["time"], unit="s")

data["vwap"] = data["price"] * data["volume"]

# resample data: it's actually faster to do these one by one (use less memory?)
ohlc = data["price"].resample(time_interval).ohlc()
vol = data["volume"].resample(time_interval).sum() #tmp var for ordering
ohlc["vwap"] = data["vwap"].resample(time_interval).sum() / vol #see on top of file for divide by 0 handling
ohlc["volume"] = vol
ohlc["count"] = data["price"].resample(time_interval).count()


# ohlc["vwap"] = ohlc["vwap"]["sum"] / ohlc["volume"]["sum"] #TODO: catch divide by 0

ohlc.index = ohlc.index.view("int64") // pd.Timedelta(1, unit="s")

# save raw data used to calculate last candle
data.truncate(
    before=pd.to_datetime(ohlc[-1:].index[0], unit="s")
).to_csv(
    unsampled_file, header=False
)

# remove last entry in resampled.csv
# if match first timestamp of ohlc
if os.path.isfile(resampled_file):
    with open(resampled_file, 'r+b') as f, mmap.mmap(
            f.fileno(), 0, access=mmap.ACCESS_WRITE) as mm:
        startofline = mm.rfind(b'\n', 0, len(mm) - 1) + 1
        if ohlc.index[0] == int(mm[startofline:startofline + 10]):
            mm.resize(startofline)

ohlc.to_csv(resampled_file, header=False, mode="a")
