"""
TODO
"""

import time
import http
import socket
from abc import abstractmethod
import krakenex

import babao.utils.log as log
import babao.config as conf
from babao.inputs.inputBase import ABCInput


class ABCKrakenInput(ABCInput):
    """
    Base class for any kraken input
    """
    __API = krakenex.API()
    API_DELAY = 3

    def __init__(self):
        super().__init__()
        self.__tick = None
        if ABCKrakenInput.__API.key == '':
            try:
                ABCKrakenInput.__API.load_key(conf.API_KEY_FILE)
            except Exception as e:  # TODO
                log.warning(
                    "Couldn't load kraken api key file '"
                    + conf.__API_KEY_FILE + "': " + repr(e)
                )

    def _doRequest(self, method, req=None):
        """General function for kraken api requests"""

        self.__sleep()
        if not req:
            req = {}

        # we loop in case of request error (503...)
        fail_counter = 1
        while fail_counter > 0:  # really nice loop bro, respect... no goto tho
            try:
                if method == "Trades":
                    res = ABCKrakenInput.__API.query_public(method, req)
                else:
                    res = ABCKrakenInput.__API.query_private(method, req)
            except (
                    socket.timeout,
                    socket.error,
                    http.client.BadStatusLine,
                    http.client.CannotSendRequest,
                    ValueError
            ) as e:
                log.warning(
                    "Network error while querying Kraken API!\n" + repr(e)
                )
            else:
                err = res.get("error", [])
                if err:
                    for e in err:
                        log.warning("Exception returned by Kraken API!\n" + e)
                else:
                    return res["result"]
            log.debug("Connection fail #" + str(fail_counter))
            fail_counter += 1
            time.sleep(0.5)

        return None  # warning-trap

    def __sleep(self):
        """TODO"""
        if self.__tick is not None:
            delta = time.time() - self.__tick
            log.debug(
                "Loop took " + str(round(delta, 3)) + "s ("
                + self.__class__.__name__ + ")"
            )
        else:
            delta = 0
        delta = self.API_DELAY - delta
        if delta > 0:
            time.sleep(delta)
        self.__tick = time.time()

    @abstractmethod
    def fetch(self):
        pass
