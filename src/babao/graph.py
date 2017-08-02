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
import babao.data.indicators as indic

MAX_POINTS = 42000  # TODO: move to config/arg
DATA = None


def updateData():
    """
    Update ´DATA´ global

    Basically merge previous data with new data in files
    """

    global DATA

    if not os.path.isfile(conf.RESAMPLED_TRADES_FILE) \
       or not os.path.isfile(conf.INDICATORS_FILE):
        log.warning("Data files not found... Is it your first time around?")
        return False

    if os.path.isfile(conf.LOCK_FILE):
        log.warning("graph.updateData(): won't update, lock file found")
        return False

    last_time = int(DATA.index.view("int64")[-1] // 1000)
    fresh_data = fu.getLinesAfter(
        conf.RESAMPLED_TRADES_FILE,
        last_time,
        conf.RESAMPLED_TRADES_COLUMNS
    )
    fresh_data = fresh_data.join(
        fu.getLinesAfter(
            conf.INDICATORS_FILE,
            last_time,
            conf.INDICATORS_COLUMNS
        )
    )
    try:
        # we assume this is a "small" file
        fresh_len = len(fresh_data)
        fresh_data = fresh_data.join(
            fu.readFile(
                conf.RESAMPLED_LEDGER_FILE,
                conf.RESAMPLED_LEDGER_COLUMNS
            ),
            how="outer"
        ).ffill().fillna(0)[-fresh_len:]
        fresh_data["bal"] = fresh_data["quote_bal"] \
            + fresh_data["crypto_bal"] * fresh_data["vwap"]
    except FileNotFoundError:
        fresh_data["crypto_bal"] = 0
        fresh_data["quote_bal"] = 0
        fresh_data["bal"] = 0
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

    if not os.path.isfile(conf.RESAMPLED_TRADES_FILE) \
       or not os.path.isfile(conf.INDICATORS_FILE):
        log.warning("Data files not found... Is it your first time around?")
        DATA = pd.DataFrame(
            columns=conf.RESAMPLED_TRADES_COLUMNS
            + conf.INDICATORS_COLUMNS
            + conf.RESAMPLED_LEDGER_COLUMNS
            + ["bal"]  # hmmm... we'll calculate this on the fly
        )
        return

    DATA = fu.getLastLines(
        conf.RESAMPLED_TRADES_FILE,
        MAX_POINTS,
        conf.RESAMPLED_TRADES_COLUMNS
    )
    DATA = DATA.join(
        fu.getLastLines(
            conf.INDICATORS_FILE,
            MAX_POINTS,
            conf.INDICATORS_COLUMNS
        )
    )
    try:
        DATA = DATA.join(
            fu.getLastLines(
                conf.RESAMPLED_LEDGER_FILE,
                MAX_POINTS,
                conf.RESAMPLED_LEDGER_COLUMNS
            ),
            how="outer"
        ).ffill().fillna(0)[-MAX_POINTS:]
        DATA["bal"] = DATA["quote_bal"] \
            + DATA["crypto_bal"] * DATA["vwap"]
    except FileNotFoundError:
        DATA["crypto_bal"] = 0
        DATA["quote_bal"] = 0
        DATA["bal"] = 0
    DATA.index = pd.to_datetime(DATA.index, unit="us")


def updateGraph(unused_counter, lines):
    """Function called (back) by FuncAnimation, will update graph"""

    if not updateData():
        return lines.values()

    for key in lines:
        lines[key].set_data(DATA.index, DATA[key])
    return lines.values()


def _initGraph():
    """Wrapped to display errors (this is running in a separate process)"""

    initData()

    fig = plt.figure()
    axes = {}
    axes["vwap"] = fig.add_subplot(3, 1, 1)
    axes["volume"] = fig.add_subplot(3, 1, 2, sharex=axes["vwap"])
    axes["bal"] = fig.add_subplot(3, 1, 3, sharex=axes["vwap"])

    lines = {}
    for key in axes:
        lines[key], = axes[key].plot(
            DATA.index,
            DATA[key],
            # "-",
            label=key,
            color="b",
            alpha=0.5
        )
        if key == "bal":
            col = "quote_bal"
            lines[col], = axes[key].plot(
                DATA.index,
                DATA[col],
                label=col,
                color="r",
                alpha=0.5
            )
        else:
            for i in range(len(indic.SMA_LOOK_BACK)):
                col = "SMA_" + key + "_" + str(i + 1)
                lines[col], = axes[key].plot(
                    DATA.index,
                    DATA[col],
                    label="SMA " + str(indic.SMA_LOOK_BACK[i]),
                    color="r",
                    alpha=0.7 - 0.2 * i
                )

    # the assignation is needed to avoid garbage collection...
    unused_cursor = MultiCursor(  # NOQA: F841
        fig.canvas,
        list(axes.values()),
        useblit=True,
        color="black",
        lw=0.5,
        horizOn=True
    )

    plt.setp(axes["vwap"].get_xticklabels(), visible=False)
    plt.setp(axes["volume"].get_xticklabels(), visible=False)
    for label in axes["bal"].xaxis.get_ticklabels():
        label.set_rotation(45)

    adf = axes["bal"].xaxis.get_major_formatter()
    adf.scaled[1. / 86400] = "%d/%m/%y %H:%M"
    adf.scaled[1. / 1440] = "%d/%m/%y %H:%M"
    adf.scaled[1. / 24] = "%d/%m/%y %H:%M"
    adf.scaled[1.] = "%d/%m/%y"
    adf.scaled[30.] = "%d/%m/%y"
    adf.scaled[365.] = "%d/%m/%y"

    y_min = DATA["vwap"].min()
    y_max = DATA["vwap"].max()
    space = (y_max - y_min) * 0.05  # 5% space up and down
    axes["vwap"].set_ylim(bottom=y_min - space, top=y_max + space)
    axes["volume"].set_ylim(bottom=0)
    axes["bal"].set_ylim(bottom=0)

    axes["vwap"].set_ylabel("EUR")
    axes["volume"].set_ylabel("BTC")
    axes["bal"].set_ylabel("EUR")

    for key in axes:
        axes[key].grid(True)
        axes[key].legend(loc="best")
        axes[key].yaxis.set_label_position("right")
        axes[key].yaxis.tick_right()

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


def initGraph():
    """Launch an awesome matplotlib graph!"""

    try:
        _initGraph()
    except:  # pylint: disable=bare-except
        # print("".join(traceback.format_exception(*(sys.exc_info))))
        traceback.print_exc()
        sys.exit(1)
