"""
TODO
"""

import time
from abc import abstractmethod

import krakenex

import babao.config as conf
import babao.utils.log as log
from babao.inputs.inputBase import ABCInput

API = None
API_DELAY = 3


def _initAPI():
    """TODO"""
    global API
    API = krakenex.API()
    try:
        API.load_key(conf.API_KEY_FILE)
    except FileNotFoundError as e:
        log.warning(
            "Couldn't load kraken api key file '"
            + conf.API_KEY_FILE + "': " + repr(e)
        )


class ABCKrakenInput(ABCInput):
    """
    Base class for any kraken input
    """

    def __init__(self):
        ABCInput.__init__(self)
        self.__tick = None
        if API is None:
            _initAPI()

    def _doRequest(self, method, req=None):
        """General function for kraken api requests"""
        if req is None:
            req = {}
        if method == "Trades":
            query = API.query_public
        else:
            query = API.query_private
        self._sleep()
        try:
            res = query(method, req, timeout=42)
            if res.get("error"):
                raise ValueError(res["error"][0])
        except (OSError, ValueError) as e:
            log.warning("Error while querying Kraken API!", e)
            return None
        return res["result"]

    def _sleep(self):
        """TODO"""
        if self.__tick is not None:
            delta = time.time() - self.__tick
            log.debug(
                "Request took " + str(round(delta, 3)) + "s ("
                + self.__class__.__name__ + ")"
            )
        else:
            delta = 0
        delta = API_DELAY - delta
        if delta > 0:
            time.sleep(delta)
        self.__tick = time.time()

    @abstractmethod
    def fetch(self):
        pass
