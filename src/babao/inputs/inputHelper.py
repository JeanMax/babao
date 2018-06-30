"""
TODO
"""

import pandas as pd

import babao.inputs.inputBase as inputBase
import babao.config as conf


def resampleSerie(s):
    """
    Call Serie.resample on s with preset parameters
    (the serie's index must be datetime)
    """
    # TODO: would be nice to do the base init once for all features
    # (ensure sync and save some computing)
    # also don't convert date or do it in utils.date
    base = pd.to_datetime(inputBase.LAST_WRITE, unit="ns")
    base = (base.minute + (base.second + 1) / 60) % 60
    return s.resample(
        str(conf.TIME_INTERVAL) + "Min",
        closed="right",
        label="right",
        base=base
    )


def readInputs(input_list, since=None, till=None, resample=False):
    """TODO"""
    # TODO: opt memory usage
    ret = []
    for inp in input_list:
        # TODO: lock once
        ret.append(
            inp.read(since, till)
        )
    if resample:
        # TODO: ensure resample base is correct (use till, or?)
        for i, inp in enumerate(input_list):
            ret[i] = inp.resample(ret[i])
    return ret
