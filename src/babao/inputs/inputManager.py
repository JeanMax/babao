"""
TODO
or is it a manager?
"""

from multiprocessing.dummy import Pool as ThreadPool
from functools import partial
from typing import List, Union

import babao.utils.file as fu
import babao.utils.log as log
import babao.inputs.inputBase as ib

POOL = None


def fetchInputs():
    """TODO: move?"""
    global POOL
    if POOL is None:
        POOL = ThreadPool(
            initializer=lambda x, y: [log.setLock(x), fu.setLock(y)],
            initargs=(log.LOCK, fu.LOCK)
        )
        # well educated people use to join & close pool
    fetched_data = POOL.map(lambda inp: inp.fetch(), ib.INPUTS)
    # TODO: catch if inputs are out of sync (then you need to stop predictModels)
    for i, _unused in enumerate(fetched_data):
        ib.INPUTS[i].write(fetched_data[i])


def readInputs(input_list: Union[List[ib.ABCInput], None] = None, since=None):
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
        df[inp_col] = inp.fillMissing(
            df.loc[:, inp_col].rename(partial_restorer, axis="columns")
        )

    return df
