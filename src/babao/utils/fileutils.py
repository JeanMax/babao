"""Some utils functions for csv handling"""

import os
import io
import mmap
import pandas as pd


def readFile(filename, names=None, dtype=None, chunksize=None):
    """Return the content of the given csv file as a DataFrame"""

    return pd.read_csv(
        filename,
        names=names,
        dtype=dtype,
        chunksize=chunksize,
        engine='c',
        memory_map=True,
        header=None,
        index_col=0
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
            start = mm.rfind(b'\n', 0, start)
            if start == -1:  # we reached the begin of file
                break

        return readFile(io.BytesIO(mm[start + 1:end]), names)


def removeLastLine(filename, timestamp):  # TODO: rename or something
    """
    Remove last entry in ´filename´ if it match ´timestamp(int)´

    Return True if an entry was actually removed
    """

    if os.path.isfile(filename):
        with open(filename, 'r+b') as f, mmap.mmap(
            f.fileno(), 0, access=mmap.ACCESS_WRITE
        ) as mm:
            end = len(mm) - 1
            last_line_pos = mm.rfind(b'\n', 0, end) + 1
            next_comma = mm.find(b',', last_line_pos, end)
            if timestamp == int(mm[last_line_pos:next_comma]):
                if last_line_pos > 0:
                    mm.resize(last_line_pos)
                else:
                    f.truncate()
                return True
    return False


def getLinesAfter(filename, timestamp, names=None):
    """
    Return all entries in ´filename´ after ´timestamp(int)´ included

    Return None if the timestamp wasn't found
    """

    with open(filename, 'r') as f, mmap.mmap(
        f.fileno(), 0, access=mmap.ACCESS_READ
    ) as mm:
        end = len(mm) - 1
        start = end
        while True:
            start = mm.rfind(b'\n', 0, start)
            next_comma = mm.find(b',', start + 1, end)
            t = int(mm[start + 1:next_comma])
            if timestamp == t:
                return readFile(io.BytesIO(mm[start + 1:]), names)
            if timestamp > t or start == -1:
                return None
