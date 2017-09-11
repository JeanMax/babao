"""
Various indicators which can be added to any serie

//www.quantinsti.com/blog/build-technical-indicators-in-python
"""


def SMA(serie, look_back_delay):
    """Simple Moving Average"""

    return serie.rolling(
        window=int(look_back_delay),
        center=False
    ).mean()


def EWMA(serie, look_back_delay):
    """Exponentially-weighted Moving Average"""

    return serie.ewm(
        span=look_back_delay,
        min_periods=int(look_back_delay) - 1,
        adjust=True,
        ignore_na=False
    ).mean()
