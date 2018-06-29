"""Some utils functions for hdf handling"""
# TODO: should we catch here the read/write errors? (cf inputBase)
# TODO: append_to_multiple/select_as_multiple

import pandas as pd
from prwlock import RWLock

LOCK = None
STORE = None


def setLock(lock):
    global LOCK
    if lock is None:
        LOCK = RWLock()
    else:
        LOCK = lock


def initStore(filename):
    """TODO"""
    global STORE
    STORE = pd.HDFStore(filename)
    # complevel=9, complib='blosc'
    for k in STORE.keys():
        STORE.create_table_index(k, optlevel=9, kind='full')  # sorry :D


def closeStore():
    """TODO"""
    if STORE is not None and STORE.is_open:
        STORE.close()


def read(frame, where=None):
    """Read a frame from the hdf database"""

    with LOCK.reader_lock():
        if where is None:
            return STORE.get(frame)
        else:
            return STORE.select(frame, where)


def write(frame, df):
    """
    Write a frame from the hdf database
    TODO
    """

    with LOCK.writer_lock():
        # TODO:
        # if type(frame) == list:
            # for i, unused in enumerate(frame):
                # STORE.append(frame[i], df[i])
        # else:
        STORE.append(frame, df)
        STORE.flush(fsync=True)


def getLastRows(frame, nrows):
    """Return ´nrows´ rows from ´filename´ as a DataFrame"""

    with LOCK.reader_lock():
        try:
            frame_len = STORE.get_storer(frame).nrows
        except AttributeError:
            return pd.DataFrame()
        return STORE.select(frame, start=frame_len - nrows)
