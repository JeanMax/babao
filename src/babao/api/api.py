"""This file will handle all the api requests"""

import babao.config as conf
import babao.utils.log as log
import babao.utils.fileutils as fu
import babao.api.kraken as kraken

# TODO: block sig INT/TERM


def initKey():
    """Call the (right) api init key"""

    kraken.initKey()


def dumpData():
    """Return a DataFrame of the last trades and append it to ´conf.RAW_FILE´"""

    log.debug("Entering dumpData()")

    raw_data = kraken.getRawTrades()
    fu.writeFile(conf.RAW_FILE, raw_data, mode="a")

    return raw_data
