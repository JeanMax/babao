"""
TODO
"""

from abc import ABC, abstractmethod
import pandas as pd

import babao.config as conf
import babao.utils.file as fu
import babao.utils.date as du
import babao.utils.log as log  # TODO: share a lock between inputs for debug
from babao.utils.rwlock import RWLock


class ABCInput(ABC):
    """
    Base class for any input

    Public attr:
    * write : self -> Bool
    * read : self -> int -> DataFrame

    Your subclass should at least implement:
    * fetch : self -> DataFrame

    And eventually: (if you want self.resample to works)
    * _resample : self -> DataFrame -> DataFrame
    * _fillMissing : self -> DataFrame -> DataFrame

    (cf. specific method doc-string in this class)
    """
    __last_write = 0
    rw_lock = RWLock()

    @property
    @abstractmethod
    def raw_columns(self):
        """TODO"""
        pass

    @property
    @abstractmethod
    def resampled_columns(self):
        """TODO"""
        pass

    def __init__(self):
        self.last_row = None
        ABCInput.rw_lock.reader_acquire()
        try:
            last_row = fu.getLastRows(
                conf.DB_FILE, self.__class__.__name__, 1
            )
        except (FileNotFoundError, KeyError):
            log.warning(
                "Couldn't read database frame for '"
                + self.__class__.__name__ + "'"
            )
            return
        finally:
            ABCInput.rw_lock.reader_release()
        self.__updateLastRow(last_row.iloc[-1])
        # TODO: msg, move to tests?
        # assert list(self.last_row.keys()) == self.__class__.raw_columns

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
        ABCInput.rw_lock.writer_acquire()
        try:
            fu.write(conf.DB_FILE, self.__class__.__name__, raw_data)
        except RuntimeError:  # HDF5ExtError
            return False
        finally:
            ABCInput.rw_lock.writer_release()
        self.__updateLastRow(raw_data.iloc[-1])
        return True

    def read(self, since=None):
        """
        TODO
        """
        if since is not None:
            since = "index > %d" % since
        ABCInput.rw_lock.reader_acquire()
        try:
            raw_data = fu.read(
                conf.DB_FILE, self.__class__.__name__, where=since
            )
        except (KeyError, FileNotFoundError):
            log.warning(
                "Couldn't read database frame for '"
                + self.__class__.__name__ + "'"
            )
            return pd.DataFrame()
        finally:
            ABCInput.rw_lock.reader_release()
        # TODO: you might want to store the read data,
        # so it can be shared accross the different models
        if not raw_data.empty:
            self.__updateLastRow(raw_data.iloc[-1])
        return raw_data

    def resample(self, raw_data):
        """
        TODO

        add this to tests:
        assert list(raw_data.columns) == self.__class__.resampled_columns
        assert isimplemented(_resample, _fillMissing)
        """
        if not raw_data.empty:
            du.to_datetime(raw_data)
            raw_data = self._resample(raw_data)
            raw_data = self._fillMissing(raw_data)
            du.to_timestamp(raw_data)
        return raw_data

    def __updateLastRow(self, last_row):
        if self.last_row is not None and last_row.name < self.last_row.name:
            return
        self.last_row = last_row
        ABCInput.__last_write = max(ABCInput.__last_write, last_row.name)

    @staticmethod
    def _resampleSerie(s):
        """
        Call Serie.resample on s with preset parameters
        (the serie's index must be datetime)
        """
        # TODO: would be nice to do the base init once for all features
        # (ensure sync and save some computing)
        # also don't convert date or do it in utils.date
        base = pd.to_datetime(ABCInput.__last_write, unit="ns")
        base = (base.minute + (base.second + 1) / 60) % 60
        return s.resample(
            str(conf.TIME_INTERVAL) + "Min",
            closed="right",
            label="right",
            base=base
        )

    def _resample(self, raw_data):
        """
        Return the DataFrame ´raw_data´ as a continuous time-serie

        ´raw_data´ is a DataFrame with the same columns as the ones returned
        by ´fetch´.

        You should use the helper function ´_resampleSerie´ on the desired
        columns of your discrete ´raw_data´ to generate continuous data.
        """
        raise NotImplementedError(
            "Your Input class '%s' should implement a '_resample' method :/"
            % self.__class__.__name__
        )

    def _fillMissing(self, resampled_data):
        """
        Fill missing values (np.nan/np.inf) in ´resampled_data´
        """
        raise NotImplementedError(
            "Your Input class '%s' should implement a '_fillMissing' method :/"
            % self.__class__.__name__
        )
