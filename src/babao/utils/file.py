"""Some utils functions for hdf handling"""

import pandas as pd

LOCK = None
STORE = None


def setLock(lock):
    """TODO"""
    global LOCK
    LOCK = lock


def initStore(filename):
    """TODO"""
    global STORE
    STORE = pd.HDFStore(filename)  # complevel=9, complib='blosc'


def maintenance():
    """TODO"""
    for k in STORE.keys():
        df = STORE.get(k)
        if not df.index.is_monotonic_increasing:
            # print(k, "is NOT sorted!!!!") # DEBUG
            df.sort_index(inplace=True)
            STORE.append(k, df, append=False)  # I *love* this argument
        STORE.create_table_index(k, optlevel=9, kind='full')


def closeStore():
    """TODO"""
    if STORE is not None and STORE.is_open:
        STORE.close()


def write(frame, df):
    """
    Write a frame from the hdf database
    TODO
    """
    ret = True
    if LOCK is not None:
        LOCK.acquire_write()
    try:
        STORE.append(frame, df)
    except RuntimeError:  # HDF5ExtError
        ret = False
    finally:
        if LOCK is not None:
            LOCK.release()
    return ret


def read(frame, where=None):
    """
    Read a frame from the hdf database
    TODO
    """
    if LOCK is not None:
        LOCK.acquire_read()
    try:
        if not STORE.is_open:  # graph proc will close store, to avoid cache
            STORE.flush(fsync=True)  # just being paranoid
            ret = pd.read_hdf(STORE.filename, frame, where=where)
        elif where is None:
            ret = STORE.get(frame)
        else:
            ret = STORE.select(frame, where)
    except (KeyError, FileNotFoundError):
        ret = pd.DataFrame()
    finally:
        if LOCK is not None:
            LOCK.release()
    return ret


def getLastRows(frame, nrows):
    """Return ´nrows´ rows from ´filename´ as a DataFrame"""
    if LOCK is not None:
        LOCK.acquire_read()
    try:
        frame_len = STORE.get_storer(frame).nrows
        ret = STORE.select(frame, start=frame_len - nrows)
    except (KeyError, FileNotFoundError, AttributeError):
        ret = pd.DataFrame()
    finally:
        if LOCK is not None:
            LOCK.release()
    return ret
