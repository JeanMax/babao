"""Some utils functions for hdf handling"""
# TODO: should we catch here the read/write errors? (cf inputBase)

import pandas as pd
from prwlock import RWLock

LOCK = None


def setLock(lock):
    global LOCK
    if lock is None:
        LOCK = RWLock()
    else:
        LOCK = lock


def read(filename, frame, where=None):
    """Read a frame from the hdf database"""

    with LOCK.reader_lock():
        return pd.read_hdf(filename, frame, where=where)


def write(filename, frame, df):
    """Write a frame from the hdf database"""

    with LOCK.writer_lock():
        return df.to_hdf(
            filename,
            frame,
            mode="a",
            format='table',
            append=True,
            # data_column=True,
            complib='blosc'
        )
        # TODO: (once)
        # store = pd.HDFStore(conf.DB_FILE)
        # store.create_table_index(conf.TRADES_FRAME, optlevel=9, kind='full')
        # store.close()


def getLastRows(filename, frame, nrows):
    """Return ´nrows´ rows from ´filename´ as a DataFrame"""

    with LOCK.reader_lock():
        # TODO: shouldn't we keep *one* open store for the whole execution?
        with pd.HDFStore(filename) as store:
            try:
                frame_len = store.get_storer(frame).nrows
            except AttributeError:
                return pd.DataFrame()

            return store.select(
                frame,
                start=frame_len - nrows
            )
