"""
TODO
"""

from typing import List
from abc import ABC, abstractmethod
import pandas as pd

import babao.utils.file as fu
import babao.utils.date as du
import babao.utils.log as log
import babao.config as conf

LAST_WRITE = 0  # TODO: this is a stupid idea, bugs incoming!


def resampleSerie(s):
    """
    Call Serie.resample on s with preset parameters
    (the serie's index must be datetime)
    """
    # TODO: would be nice to do the base init once for all features
    # (ensure sync and save some computing)
    # also don't convert date or do it in utils.date
    base = pd.to_datetime(LAST_WRITE, unit="ns")
    base = (base.minute + (base.second + 1) / 60) % 60
    return s.resample(
        str(conf.TIME_INTERVAL) + "Min",
        closed="right",
        label="right",
        base=base
    )


class ABCInput(ABC):
    """
    TODO
    Base class for any input

    Public attr:
    * write : self -> Bool
    * read : self -> int -> DataFrame

    Your subclass should at least implement:
    * fetch : self -> DataFrame

    And eventually: (if you want self.resample to works)
    * _resample : self -> DataFrame -> DataFrame
    * fillMissing : self -> DataFrame -> DataFrame

    (cf. specific method doc-string in this class)
    """

    @property
    @abstractmethod
    def raw_columns(self) -> List[str]:
        """TODO"""
        pass

    @property
    @abstractmethod
    def resampled_columns(self) -> List[str]:
        """TODO"""
        pass

    def __init__(self):
        # TODO: msg, move to tests?
        # assert list(self.last_row.keys()) == self.__class__.raw_columns
        self.last_row = None
        self.__cache_data = None
        last_row = fu.getLastRows(self.__class__.__name__, 1)
        if not last_row.empty:
            self.__updateLastRow(last_row.iloc[-1])
        else:
            log.warning(
                "Couldn't read from database frame '"
                + self.__class__.__name__ + "'"
            )

    @abstractmethod
    def fetch(self):
        """
        Return a time-serie DataFrame fetched from the internets

        This data will be stored on database for later use (and eventual
        resampling).
        Data can be continuous.
        Index must be nanosecond timestamps.
        """
        raise NotImplementedError(
            "Your Input class '%s' should implement a 'fetch' method :/"
            % self.__class__.__name__
        )

    def write(self, raw_data):
        """
        TODO
        """
        if raw_data is None or raw_data.empty:
            return None
        if not fu.write(self.__class__.__name__, raw_data):
            log.warning(
                "Couldn't write to database frame '"
                + self.__class__.__name__ + "'"
            )
            return False
        self.__updateLastRow(raw_data.iloc[-1])
        return True

    def read(self, since=None, till=None):
        """
        TODO
        """
        if self.__cache_data is not None:
            raw_data = self.__cache_data.loc[since:till]
        else:
            where = None
            if since is not None:
                where = "index > %d" % since
            if till is not None:
                where += " & index < %d" % till
            raw_data = fu.read(self.__class__.__name__, where=where)
        if not raw_data.empty:
            self.__updateLastRow(raw_data.iloc[-1])
        return raw_data

    def cache(self, since=None, till=None, data=None):
        """TODO"""
        if data is not None:
            self.__cache_data = data
        else:
            self.__cache_data = None
            self.__cache_data = self.read(since, till)

    def resample(self, raw_data):
        """
        TODO

        add this to tests:
        assert list(raw_data.columns) == self.__class__.resampled_columns
        assert isimplemented(_resample, fillMissing)
        """
        if raw_data.empty:
            return pd.DataFrame(columns=self.resampled_columns)
        du.to_datetime(raw_data)
        resampled_data = self._resample(raw_data)
        resampled_data = self.fillMissing(resampled_data)
        du.to_timestamp(raw_data)
        du.to_timestamp(resampled_data)
        return resampled_data

    def __updateLastRow(self, last_row):
        if self.last_row is not None and last_row.name < self.last_row.name:
            return
        self.last_row = last_row
        global LAST_WRITE
        LAST_WRITE = max(LAST_WRITE, last_row.name)

    def _resample(self, raw_data):
        """
        Return the DataFrame ´raw_data´ as a continuous time-serie

        ´raw_data´ is a DataFrame with the same columns as the ones returned
        by ´fetch´.

        You should use the helper function ´resampleSerie´ on the desired
        columns of your discrete ´raw_data´ to generate continuous data.

        TODO
        """
        raise NotImplementedError(
            "Your Input class '%s' should implement a '_resample' method :/"
            % self.__class__.__name__
        )

    def fillMissing(self, resampled_data):
        """
        Fill missing values (np.nan/np.inf) in ´resampled_data´
        """
        raise NotImplementedError(
            "Your Input class '%s' should implement a 'fillMissing' method :/"
            % self.__class__.__name__
        )
