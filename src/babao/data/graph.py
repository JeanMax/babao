"""Data visualisation inside"""

import os
import sys
import time
import traceback
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import MultiCursor

import babao.config as conf
import babao.utils.log as log
import babao.utils.fileutils as fu

MAX_POINTS = 42000  # TODO: move to config/arg
DATA = None


def updateData():
    """
    Update ´DATA´ global

    Basically merge previous data with new data in files
    """

    global DATA

    if not os.path.isfile(conf.RESAMPLED_FILE) \
       or not os.path.isfile(conf.INDICATORS_FILE):
        log.warning("Data files not found... Is it your first time around?")
        return False

    if os.path.isfile(conf.LOCK_FILE):
        log.warning("graph.updateData(): won't update, lock file found")
        return False

    last_time = int(DATA.index.view("int64")[-1] // 1000)
    fresh_data = fu.getLinesAfter(
        conf.RESAMPLED_FILE,
        last_time,
        conf.RESAMPLED_COLUMNS
    )
    fresh_data = fresh_data.join(
        fu.getLinesAfter(
            conf.INDICATORS_FILE,
            last_time,
            conf.INDICATORS_COLUMNS
        )
    )
    fresh_data.index = pd.to_datetime(fresh_data.index, unit="us")

    DATA = DATA.iloc[:-1].append(fresh_data).iloc[-MAX_POINTS:]

    return True


def initData():
    """
    Initialize ´DATA´ global

    Basically read ´MAX_POINTS´ from data files
    """

    global DATA

    # init lock file
    while os.path.isfile(conf.LOCK_FILE):
        time.sleep(0.1)

    if not os.path.isfile(conf.RESAMPLED_FILE) \
       or not os.path.isfile(conf.INDICATORS_FILE):
        log.warning("Data files not found... Is it your first time around?")
        DATA = pd.DataFrame(
            columns=conf.RESAMPLED_COLUMNS + conf.INDICATORS_COLUMNS
        )
        return

    DATA = fu.getLastLines(
        conf.RESAMPLED_FILE,
        MAX_POINTS,
        conf.RESAMPLED_COLUMNS
    )
    DATA = DATA.join(
        fu.getLastLines(
            conf.INDICATORS_FILE,
            MAX_POINTS,
            conf.INDICATORS_COLUMNS
        )
    )
    DATA.index = pd.to_datetime(DATA.index, unit="us")


def updateGraph(unused_counter, lines):
    """Function called (back) by FuncAnimation, will update graph"""

    try:
        if not updateData():
            return lines.values()

        for key in lines:
            lines[key].set_data(DATA.index, DATA[key])
    except:  # pylint: disable=bare-except
        # running in a separate process, so we need tricks to display errors
        # print("".join(traceback.format_exception(*(sys.exc_info))))
        traceback.print_exc()
        sys.exit(1)

    return lines.values()


def initGraph():
    """Launch an awesome matplotlib graph!"""

    initData()

    fig = plt.figure()
    axes = {}
    axes["price"] = fig.add_subplot(2, 1, 1)
    axes["volume"] = fig.add_subplot(2, 1, 2, sharex=axes["price"])

    lines = {}
    lines["vwap"], = axes["price"].plot_date(
        DATA.index,
        DATA["vwap"],
        "-",
        label="vwap",
        color="b",
        alpha=0.7
    )
    lines["SMA_7"], = axes["price"].plot_date(
        DATA.index,
        DATA["SMA_7"],
        "-",
        label="SMA_7",
        color="r",
        alpha=0.7
    )

    lines["volume"], = axes["volume"].plot_date(
        DATA.index,
        DATA["volume"],
        "-",
        label="volume",
        color="g",
        alpha=0.7
    )

    # slow and ugly, plus there is something wrong with date format
    # candlestick_ohlc(
    #    axes["price"], DATA.values,
    #    width=0.05, colorup='g', colordown='r'
    # )

    unused_cursor = MultiCursor(  # NOQA: F841
        fig.canvas,
        list(axes.values()),
        useblit=True,
        color='black',
        lw=0.5,
        horizOn=True
    )

    plt.setp(axes["price"].get_xticklabels(), visible=False)
    for label in axes["volume"].xaxis.get_ticklabels():
        label.set_rotation(45)

    adf = axes["volume"].xaxis.get_major_formatter()
    adf.scaled[1./86400] = '%d/%m/%y %H:%M'
    adf.scaled[1./1440] = '%d/%m/%y %H:%M'
    adf.scaled[1./24] = '%d/%m/%y %H:%M'
    adf.scaled[1.] = '%d/%m/%y'
    adf.scaled[30.] = '%d/%m/%y'
    adf.scaled[365.] = '%d/%m/%y'

    axes["price"].set_ylim(
        bottom=DATA["vwap"].min()
        - (axes["price"].get_ylim()[1] - DATA["vwap"].max())
    )

    axes["price"].set_ylabel("EUR")
    axes["volume"].set_ylabel("BTC")

    for key in axes:
        axes[key].grid(True)
        axes[key].legend(loc="best")
        axes[key].yaxis.set_label_position("right")
        axes[key].yaxis.tick_right()

        # won't update ticks when zooming :(
        # import numpy as np
        # axes[key].yaxis.set_ticks(
        #     np.append(
        #         axes[key].yaxis.get_majorticklocs(),
        #         DATA[key].iloc[-1]
        #     )
        # )

        # not so good when zooming in :/
        # last_x = DATA.index[-1]
        # last_y = DATA[key].iloc[-1]
        # axes[key].annotate(
        #     str(int(last_y)),
        #     (last_x, last_y),
        #     xytext=(
        #         last_x + (last_x - DATA.index[-int(MAX_POINTS / 4)]),
        #         last_y
        #     ),
        #     bbox={"boxstyle": "larrow"}
        # )
        # lines[key + "last"] = axes[key].axhline(
        #     y=last_y,
        #     color="b",
        #     linewidth=0.5
        # )

    plt.subplots_adjust(top=0.97, left=0.03, right=0.92, hspace=0.05)

    # the assignations are needed to avoid garbage collection...
    unused_animation = animation.FuncAnimation(  # NOQA: F841
        fig,
        updateGraph,
        fargs=(lines,),
        # blit=True,  # bug?
        interval=2500
    )
    plt.show()  # this is blocking!
