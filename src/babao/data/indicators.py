"""Add various indicators to the resampled trade data"""

import pandas as pd

import babao.config as conf
import babao.utils.log as log
import babao.utils.fileutils as fu

MAX_LOOK_BACK = 77  # TODO: I'm not sure how to handle that


# I think you should differentiate actual parameters from data parameter
def indicator_SMA(close_price, look_back_delay):
    """Simple Moving Average"""

    return close_price.rolling(
        window=look_back_delay,
        center=False
    ).mean()


# idem
def indicator_EWMA(close_price, look_back_delay):
    """Exponentially-weighted Moving Average"""

    return close_price.ewm(
        span=look_back_delay,
        min_periods=look_back_delay - 1,
        adjust=True,
        ignore_na=False
    ).mean()


# https://www.quantinsti.com/blog/build-technical-indicators-in-python
def updateIndicators(numberOfLinesToRead):
    """
    Update indicators for the freshly fetched (and resampled) data
    ´numberOfLinesToRead´ is the number of entries resampled without indicators
    """

    log.debug("Entering updateIndicators()")

    resampled_data = fu.getLastLines(
        conf.RESAMPLED_FILE,
        numberOfLinesToRead + MAX_LOOK_BACK,
        names=conf.RESAMPLED_COLUMNS
    )

    close = resampled_data['close']  # TODO: test if this is really faster
    indicators_data = pd.DataFrame()

    for i in [3, 5, 7]:
        indicators_data["SMA_" + str(i)] = indicator_SMA(close, i)
        indicators_data["EWMA_" + str(i)] = indicator_EWMA(close, i)

    indicators_data.index = resampled_data.index

    # removing extra data used for calculations
    # TODO: find a way to optimize that:
    # you need the resampled data for the indicators,
    # but you don't want to recalculate the indicators already computed)
    indicators_data = indicators_data.tail(numberOfLinesToRead)

    fu.removeLastLine(conf.INDICATORS_FILE, int(indicators_data.index[0]))
    fu.writeFile(conf.INDICATORS_FILE, indicators_data, mode="a")

    return indicators_data
