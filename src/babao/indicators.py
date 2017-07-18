"""TODO"""

import pandas as pd

import babao.log as log
import babao.config as conf
import babao.fileutils as fu

MAX_LOOK_BACK = 77  # TODO: I'm not sure how to handle that


# https://www.quantinsti.com/blog/build-technical-indicators-in-python
def updateIndicators(numberoflinestoread):
    """TODO that's a  really sweet arg name"""
    log.debug("Entering updateIndicators()")

    # I think you should differentiate actual parameters from data parameter

    # Simple Moving Average
    def indicator_SMA(close_price, look_back_delay):
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

    # TODO: NaN: df.ffill()

    resampled_data = fu.getLastLines(
        conf.RESAMPLED_FILE,
        numberoflinestoread + MAX_LOOK_BACK,
        names=[
            "time", "open", "high", "low", "close", "vwap", "volume", "count"
        ]
    )

    # indicators = {
    #     "SMA": indicator_SMA,
    #     "EWMA": indicator_EWMA
    # }
    # indicators_data = {}
    # # there might be a better way to do that...
    # for indicator_name, indicator_fun in sorted(indicators.items()):
    #     indicators_data[indicator_name] = indicator_fun(resampled_data)

    close = resampled_data['close']  # TODO: test if this is really faster
    indicators_data = pd.DataFrame()

    for i in [3, 5, 7]:
        indicators_data["SMA_" + str(i)] = indicator_SMA(close, i)
        indicators_data["EWMA_" + str(i)] = indicator_EWMA(close, i)

    indicators_data.index = resampled_data.index

    ret = resampled_data.join(indicators_data)

    # removing extra data used for calculations
    # TODO: find a way to optimize that:
    # you need the resampled data for the indicators,
    # but you don't want to recalculate the indicators already computed)
    indicators_data = indicators_data[-numberoflinestoread:]

    fu.removeLastLine(conf.INDICATORS_FILE, indicators_data.index[0])
    fu.writeFile(conf.INDICATORS_FILE, indicators_data, mode="a")

    return ret
