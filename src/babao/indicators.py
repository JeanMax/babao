"""TODO"""

import pandas as pd

import babao.log as log
import babao.config as conf

# https://www.quantinsti.com/blog/build-technical-indicators-in-python
def updateIndicators():
    """TODO"""
    log.debug("Entering updateIndicators()") # DEBUG


    # Simple Moving Average
    def indicator_SMA(close_price, look_back_delay): # I think you should differentiate actual parameters from data parameter
        """TODO"""
        return close_price.rolling(
            window=look_back_delay,
            center=False
        ).mean()

    # Exponentially-weighted Moving Average
    def indicator_EWMA(close_price, look_back_delay):
        """TODO"""
        return close_price.ewm(
            span=look_back_delay,
            min_periods=look_back_delay - 1,
            adjust=True,
            ignore_na=False
        ).mean()

    #TODO: NaN
    resampled_data = pd.read_csv(
        conf.RESAMPLED_FILE,
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
    indicators_data.to_csv(conf.INDICATORS_FILE, header=False, mode="a")

    #TODO: remove last entry as in resample.py

    return indicators_data      # DEBUG
