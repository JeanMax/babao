"""Add various indicators to the resampled trade data"""

import pandas as pd

import babao.config as conf
import babao.utils.log as log
import babao.utils.fileutils as fu

# these should be trained
SMA_LOOK_BACK = [9, 26, 77]
MAX_LOOK_BACK = SMA_LOOK_BACK[-1]


def indicator_SMA(column, look_back_delay):
    """Simple Moving Average"""

    return column.rolling(
        window=look_back_delay,
        center=False
    ).mean()


def indicator_EWMA(column, look_back_delay):
    """Exponentially-weighted Moving Average"""

    return column.ewm(
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

    indicators_data = pd.DataFrame()
    # pylint: disable=consider-using-enumerate
    for i in range(len(SMA_LOOK_BACK)):
        for col in ["vwap", "volume"]:
            indicators_data["SMA_" + col + "_" + str(i + 1)] = indicator_SMA(
                resampled_data[col],
                SMA_LOOK_BACK[i]
            )

    indicators_data.index = resampled_data.index

    # removing extra data used for calculations
    # TODO: find a way to optimize that:
    # you need the resampled data for the indicators,
    # but you don't want to recalculate the indicators already computed)
    indicators_data = indicators_data.tail(numberOfLinesToRead)

    fu.removeLastLine(conf.INDICATORS_FILE, int(indicators_data.index[0]))
    fu.writeFile(conf.INDICATORS_FILE, indicators_data, mode="a")

    return indicators_data
