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


def MACD(serie, fast_delay, slow_delay, signal_delay, full=False):
    """Moving Average Convergence/Divergence Oscillator"""

    macd_line = EWMA(serie, fast_delay) - EWMA(serie, slow_delay)
    signal_line = EWMA(macd_line, signal_delay)

    if full:
        return (macd_line, signal_line, macd_line - signal_line)
    return macd_line - signal_line


def PPO(serie, fast_delay, slow_delay, signal_delay, full=False):
    """
    Percentage Price Oscillator

    Same as MACD, but we do (a-b)/b instead of a-b,
    so the final value does not depend on input scale (it's a percentage!)
    """

    lag_line = EWMA(serie, slow_delay)
    ppo_line = (EWMA(serie, fast_delay) - lag_line) / lag_line
    signal_line = EWMA(ppo_line, signal_delay)

    if full:
        return (ppo_line, signal_line, ppo_line - signal_line)
    return ppo_line - signal_line


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
