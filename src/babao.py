"""TODO"""

import os
import time

import config as conf
import api
import resample as resamp
import indicators as indic


def mainLoop():
    time_interval = str(conf.TIME_INTERVAL) + "Min"

    resamp.resampleData(api.dumpData(), time_interval) #TODO: this could use a renaming
    indic.updateIndicators(time_interval)



def main():
    conf.readConf()

    for directory in [conf.LOG_DIR, conf.DATA_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)

    while True:
        mainLoop()
        time.sleep(3)


main()
