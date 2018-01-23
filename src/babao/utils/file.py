"""Some utils functions for hdf handling"""


import pandas as pd
import time


def read(filename, frame, where=None):
    """Read a frame from the hdf database"""

    return pd.read_hdf(filename, frame, where=where)


def write(filename, frame, df):
    """Write a frame from the hdf database"""

    # ugly workaround in case the graph is reading the database...
    for retry in range(30):
        try:
            df.to_hdf(
                filename,
                frame,
                mode="a",
                format='table',
                append=True,
                # data_column=True,
                # complib='blosc',
                # TODO: compression isn't really required,
                #       but it's not much slower
            )
            return True
        except RuntimeError:  # HDF5ExtError
            time.sleep(0.1)

    # TODO: (once)
    # store = pd.HDFStore(conf.DB_FILE)
    # store.create_table_index(conf.TRADES_FRAME, optlevel=9, kind='full')
    # store.close()

    return False


def getLastRows(filename, frame, nrows):
    """Return ´nrows´ rows from ´filename´ as a DataFrame"""

    with pd.HDFStore(filename) as store:
        try:
            frame_len = store.get_storer(frame).nrows
        except AttributeError:
            return pd.DataFrame()

        return store.select(
            frame,
            start=frame_len - nrows
        )
