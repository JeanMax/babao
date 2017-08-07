import pandas as pd
import os
import pytest

import babao.utils.fileutils as fu


def test_readFile():
    filename = "/tmp/test_readFile.csv"
    with open(filename, "w") as f:
        f.write("0,1,2\n1,3,4\n2,5,6\n")

    df = fu.readFile(filename)
    assert not df.empty
    assert len(df.index) == 3
    assert df[1][0] == 1
    assert df[2][2] == 6

    os.remove(filename)


def test_writeFile():
    filename = "/tmp/test_writeFile.csv"
    fu.writeFile(
        filename,
        pd.DataFrame(data={"x": [1, 3, 5], "y": [2, 4, 6]}, index=range(3))
    )

    df = pd.read_csv(filename, header=None, index_col=0)
    assert not df.empty
    assert len(df.index) == 3
    assert df[1][0] == 1
    assert df[2][2] == 6

    os.remove(filename)


def test_getLastLines():
    filename = "/tmp/test_getLastLines.csv"
    with open(filename, "w") as f:
        f.write("0,1,2\n1,3,4\n2,5,6\n")

    df = fu.getLastLines(filename, 1)
    assert not df.empty
    assert len(df.index) == 1
    assert df[2][2] == 6

    df = fu.getLastLines(filename, 2)
    assert not df.empty
    assert len(df.index) == 2
    assert df[1][1] == 3
    assert df[2][2] == 6

    df = fu.getLastLines(filename, 4)
    assert not df.empty
    assert len(df.index) == 3
    assert df[1][0] == 1
    assert df[1][1] == 3
    assert df[2][2] == 6

    os.remove(filename)


def test_removeLastLine():
    filename = "/tmp/test_removeLastLine.csv"
    with open(filename, "w") as f:
        f.write("1123456789,1,2\n2123456789,3,4\n")

    fu.removeLastLine(filename, 1123456789)
    df = pd.read_csv(filename, header=None, index_col=0)
    assert not df.empty
    assert len(df.index) == 2

    fu.removeLastLine(filename, 2123456789)
    df = pd.read_csv(filename, header=None, index_col=0)
    assert not df.empty
    assert len(df.index) == 1
    assert df.index[0] == 1123456789

    fu.removeLastLine(filename, 1123456789)
    with pytest.raises(pd.errors.EmptyDataError):
        df = pd.read_csv(filename, header=None, index_col=0)

    os.remove(filename)


def test_getLinesAfter():
    filename = "/tmp/test_getLinesAfter.csv"
    with open(filename, "w") as f:
        f.write("0,1,2\n1,3,4\n2,5,6\n")

    df = fu.getLinesAfter(filename, 2)
    assert not df.empty
    assert len(df.index) == 1
    assert df[2][2] == 6

    df = fu.getLinesAfter(filename, 1)
    assert not df.empty
    assert len(df.index) == 2
    assert df[1][1] == 3
    assert df[2][2] == 6

    df = fu.getLinesAfter(filename, 0)
    assert not df.empty
    assert len(df.index) == 3
    assert df[1][0] == 1
    assert df[1][1] == 3
    assert df[2][2] == 6

    df = fu.getLinesAfter(filename, -1)
    assert df is None

    df = fu.getLinesAfter(filename, 3)
    assert df is None

    os.remove(filename)
