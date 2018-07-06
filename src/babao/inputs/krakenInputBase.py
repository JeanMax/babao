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

        # we loop in case of request error (503...)
        fail_counter = 0
        while True:  # TODO: do you really want an infinite loop?
            self._sleep()
            try:
                res = query(method, req, timeout=42)
            except (OSError, ValueError) as e:
                log.warning(
                    "Network error while querying Kraken API!\n" + repr(e)
                )
            else:
                err = res.get("error", [])
                if err:
                    for er in err:
                        log.warning("Exception returned by Kraken API!\n" + er)
                else:
                    return res["result"]
            fail_counter += 1
            if not fail_counter % 10:
                _initAPI()  # have you tried turning it off and on again?
            log.debug("Connection fail #" + str(fail_counter))

        return None  # warning-trap

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
