"""Some utils functions for csv handling"""

import os
import io
import mmap
import pandas as pd


def readFile(filename, names=None):
    """Return the content of the given csv file as a DataFrame"""

    return pd.read_csv(
        filename,
        engine='c',
        header=None,
        parse_dates=True,
        index_col=0,
        names=names
    )


def writeFile(filename, df, mode="w"):
    """Write the given DataFrame ´df´ as csv file named ´filename´"""

    df.to_csv(filename, header=False, mode=mode)


def getLastLines(filename, numberoflines, names=None):
    """Return ´numberoflines´ lines from ´filename´ as a DataFrame"""

    with open(filename, 'r') as f, mmap.mmap(
        f.fileno(), 0, access=mmap.ACCESS_READ
    ) as mm:
        end = len(mm) - 1
        start = end
        for unused_counter in range(numberoflines):
            start = mm.rfind(b'\n', 0, start)  # TODO: catch errors?
        # the while loop is slower, so we'll keep the unused var...

        return readFile(io.BytesIO(mm[start + 1:end]), names)


def removeLastLine(filename, timestamp):  # TODO: rename or something
    """Remove last entry in ´filename´ if it match ´timestamp´"""

    if os.path.isfile(filename):  # TODO: catch exception instead?
        with open(filename, 'r+b') as f, mmap.mmap(
            f.fileno(), 0, access=mmap.ACCESS_WRITE
        ) as mm:
            last_line_pos = mm.rfind(b'\n', 0, len(mm) - 1) + 1
            # timestamps are formated to 10 digits
            if timestamp == int(mm[last_line_pos:last_line_pos + 10]):
                mm.resize(last_line_pos)
