"""
Various indicators which can be added to any serie

//www.quantinsti.com/blog/build-technical-indicators-in-python
"""

import sys


def SMA(serie, look_back_delay):
    """Simple Moving Average"""

    return serie.rolling(
        window=int(look_back_delay),
        center=False
    ).mean()


def EWMA(serie, look_back_delay):
    """Exponentially-weighted Moving Average"""

    return serie.ewm(
        span=int(look_back_delay),
        min_periods=int(look_back_delay) - 1,
        adjust=True,
        ignore_na=False
    ).mean()


def MACD(serie, look_back_a_delay, look_back_b_delay, signal_delay):
    """Moving Average Convergence/Divergence Oscillator"""

    # should we return these aswell?
    macd_line = EWMA(serie, look_back_a_delay) - EWMA(serie, look_back_b_delay)
    signal_line = EWMA(macd_line, signal_delay)

    return macd_line - signal_line


def get(df, columns):
    """
    Add indicators specified by columns to the given df

    Expected ´columns´ format: ["SMA_vwap_42", "EWMA_volume_12"]
    """

    for indic_col in columns:
        a = indic_col.split("_")
        fun, args = a[0], (df[a[1]], *tuple(a[2:]))
        df[indic_col] = getattr(sys.modules[__name__], fun)(*args)

    return df
