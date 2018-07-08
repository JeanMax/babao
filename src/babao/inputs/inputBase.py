"""
TODO
"""

from abc import ABC, abstractmethod
from typing import List

import pandas as pd

import babao.config as conf
import babao.utils.date as du
import babao.utils.file as fu
import babao.utils.log as log

INPUTS = []  # type: List[ABCInput]
LAST_WRITE = 0  # TODO: this is a stupid idea, bugs incoming!


def resampleSerie(s):
    """
    Call Serie.resample on s with preset parameters
    (the serie's index must be datetime)
    """
    # TODO: would be nice to do the base init once for all features
    # (ensure sync and save some computing)
    # also don't convert date or do it in utils.date
    base = du.to_datetime(LAST_WRITE)
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
        # assert list(self.current_row.keys()) == self.__class__.raw_columns
        self.up_to_date = True
        self.__cache_data = None
        self.current_row = None
        last_row = fu.getLastRows(self.__class__.__name__, 1)
        if not last_row.empty:
            self.updateCurrentRow(last_row.iloc[-1])
            # TODO: remove read once cache implemented
        else:
            log.warning("Database '" + self.__class__.__name__ + "' is emtpy")

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
        self.updateCurrentRow(raw_data.iloc[-1])
        return True

    def read(self, since=None, till=None):
        """
        TODO
        """
        if till is None or till > du.getTime():
            till = du.NOW
        if self.__cache_data is not None:
            raw_data = self.__cache_data.loc[since:till]
        else:
            where = None
            if since is not None:
                where = "index > %d" % since
            if till is not None:
                where += " & index < %d" % till
            raw_data = fu.read(self.__class__.__name__, where=where)
        return raw_data

    def cache(self, since=None, data=None):
        """TODO"""
        if data is not None:
            self.__cache_data = data
        else:
            self.__cache_data = None
            self.__cache_data = self.read(since)

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

    def updateCurrentRow(self, current_row=None, timestamp=None):
        """TODO"""
        global LAST_WRITE
        if timestamp is not None:
            loosy_interval = du.secToNano(12 * 3600)
            current_row = self.read(
                since=timestamp - loosy_interval,
                till=timestamp + loosy_interval
                # assuming there is one row per day?
            )
            if not current_row.empty:
                current_row = current_row.iloc[0]
        if not current_row.empty:
            self.current_row = current_row
            if timestamp is not None:
                LAST_WRITE = max(LAST_WRITE, current_row.name)
            else:
                LAST_WRITE = current_row.name  # time travel
        # else:  # spammy
        #     log.warning(
        #         "Couldn't update current row for database  '"
        #         + self.__class__.__name__ + "'"
        #     )

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
