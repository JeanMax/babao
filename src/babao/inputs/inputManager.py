"""
Common interface to inputs to call methods on all of them at once
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
    """
    Make sure the cache is up to date on the given inputs
    (or all the INPUTS)
    """
    if input_list is None:
        input_list = ib.INPUTS
    for inp in ib.INPUTS:
        inp.refreshCache()


def fetchInputs():
    """
    Fetch all the INPUTS in a pool thread

    The raw data resulting is then wrote to database.
    """
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
    """
    Read all INPUTS from ´since´ and resample them with matching time base

    The return is one dataframe containing all concatened columns (so they will
    be renamed with the input name as prefix
    """

    def _renamer(prefix, s):
        """
        Rename a column to avoid name collisions
        (add input name as prefix)
        """
        return prefix + "-" + s

    def _restorer(prefix, s):
        """Restore the original name of a column (remove prefix)"""
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
    """Travel to the specified timestamp, for simulation purposes"""
    du.TIME_TRAVELER.setTime(timestamp)
    for i in ib.INPUTS:
        i.updateCurrentRow(timestamp=timestamp)
