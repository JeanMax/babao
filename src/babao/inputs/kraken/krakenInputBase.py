"""
TODO
"""

import time
import http
import socket
from abc import abstractmethod
import krakenex

import babao.config as conf
import babao.utils.log as log  # TODO: share a lock between inputs for debug
from babao.inputs.inputBase import ABCInput


class ABCKrakenInput(ABCInput):
    """Base class for any kraken input"""
    __k = krakenex.API()

    def __init__(self):
        super().__init__()
        if ABCKrakenInput.__k.key == '':
            try:
                ABCKrakenInput.__k.load_key(conf.API_KEY_FILE)
            except Exception as e:  # DEBUG
                log.warning(
                    "Couldn't load kraken api key file '"
                    + conf.API_KEY_FILE + "': " + repr(e)
                )      # DEBUG

    def _doRequest(self, method, req=None):
        """General function for kraken api requests"""

        if not req:
            req = {}

        # we loop in case of request error (503...)
        fail_counter = 1
        while fail_counter > 0:  # really nice loop bro, respect... no goto tho
            try:
                if method == "Trades":
                    res = ABCKrakenInput.__k.query_public(method, req)
                else:
                    res = ABCKrakenInput.__k.query_private(method, req)
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

    @abstractmethod
    def fetch(self):
        pass
