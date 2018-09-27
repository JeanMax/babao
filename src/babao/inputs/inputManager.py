"""
TODO
or is it a manager?
"""

from multiprocessing.dummy import Pool as ThreadPool
from functools import partial, reduce
from typing import List, Optional, Union

import babao.utils.date as du
import babao.utils.file as fu
import babao.utils.log as log
import babao.inputs.inputBase as ib

POOL = None


def refreshInputs(input_list: Union[List[ib.ABCInput], None] = None):
    """TODO"""
    if input_list is None:
        input_list = ib.INPUTS
    for inp in ib.INPUTS:
        inp.refreshCache()


def fetchInputs():
    """TODO"""
    global POOL
    if POOL is None:
        POOL = ThreadPool(
            initializer=lambda x, y: [log.setLock(x), fu.setLock(y)],
            initargs=(log.LOCK, fu.LOCK)
        )
        # well educated people use to join & close pool
    fetched_data_list = POOL.map(lambda inp: inp.fetch(), ib.INPUTS)
    for inp, fetched_data in zip(ib.INPUTS, fetched_data_list):
        inp.write(fetched_data)
    return reduce(lambda acc, inp: acc & inp.up_to_date, ib.INPUTS, True)


def readInputs(input_list: Optional[List[ib.ABCInput]] = None, since=None):
    """TODO"""

    def _renamer(prefix, s):
        """TODO"""
        return prefix + "-" + s

    def _restorer(prefix, s):
        """TODO"""
        return s.replace(prefix + "-", "")

    if input_list is None:
        input_list = ib.INPUTS

    # TODO: opt memory usage / lock once
    data_list = [inp.read(since) for inp in input_list]

    # TODO: ensure resample base is correct (use till, or?)
    for i, inp in enumerate(input_list):
        data_list[i] = inp.resample(data_list[i])
        partial_renamer = partial(_renamer, inp.__class__.__name__)
        data_list[i].rename(partial_renamer, axis="columns", inplace=True)

    df = data_list[0].join(data_list[1:], how="outer")

    for inp in input_list:
        partial_restorer = partial(_restorer, inp.__class__.__name__)
        partial_renamer = partial(_renamer, inp.__class__.__name__)
        inp_col = [partial_renamer(col) for col in inp.resampled_columns]
        if not df[inp_col].empty:
            df[inp_col] = inp.fillMissing(
                df.loc[:, inp_col].rename(partial_restorer, axis="columns")
            )

    return df


def timeTravel(timestamp):
    """TODO"""
    du.setTime(timestamp)
    for i in ib.INPUTS:
        i.updateCurrentRow(timestamp=timestamp)
