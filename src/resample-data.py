#!/usr/bin/env python

# time,open,high,low,close,vwap,volume,count

import os #path.isfile
import sys #argv
import mmap
import pandas as pd

#the file given as parameter is just the last data, not the whole file

#TODO: bitch about wrong argv usage

# data_file="~/babao/data/trade-XXBTZEUR.csv" #TODO: sys.argv[1]
# time_interval="1Min" #TODO: sys.argv[2] + "Min"

data_file=sys.argv[1]
time_interval=sys.argv[2] + "Min"

unsampled_file=sys.argv[3] + "-unsampled-" + time_interval + ".csv"
resampled_file=sys.argv[3] + "-resampled-" + time_interval + ".csv"

# current raw data file
data = pd.read_csv(
    data_file,
    names=["time", "price", "volume"],
    engine='c',
    parse_dates=True,
    # header=1 #TODO: be sure there is no header
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

# resampled data
ohlc = data["price"].resample(time_interval).ohlc()
ohlc["vwap"] = data["price"].resample(time_interval).mean() #TODO
ohlc["volume"] = data["volume"].resample(time_interval).sum()
ohlc["count"] = data["price"].resample(time_interval).count()

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
