"""Data visualisation inside"""

import os
import time
import traceback
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import MultiCursor

import babao.utils.fileutils as fu
import babao.utils.log as log
import babao.utils.lock as lock
import babao.config as conf
import babao.data.indicators as indic

DATA = None


def _resampleLedgerAndJoinTo(resampled_data):
    """
    Resample ´conf.RAW_LEDGER_FILE´ and join it to ´resampled_data´

    Only entries included in ´resampled_data.index´ time window will be joined
    Return the result of this join
    """

    try:
        raw_ledger = fu.readFile(
            conf.RAW_LEDGER_FILE,
            conf.RAW_LEDGER_COLUMNS
        )
        raw_ledger.index = pd.to_datetime(raw_ledger.index, unit="us")
        for col in raw_ledger.columns:
            if col not in conf.RESAMPLED_LEDGER_COLUMNS:
                del raw_ledger[col]
        resampled_ledger = raw_ledger.resample(
            str(conf.TIME_INTERVAL) + "Min"
        ).last()

        resampled_data_first = resampled_data.index[0]
        resampled_data_last = resampled_data.index[-1]
        resampled_data = resampled_data.join(
            resampled_ledger,
            how="outer"
        ).ffill().fillna(0).loc[resampled_data_first:resampled_data_last]

        resampled_data["bal"] = resampled_data["quote_bal"] \
            + resampled_data["crypto_bal"] * resampled_data["vwap"]
    except FileNotFoundError:
        resampled_data["crypto_bal"] = 0
        resampled_data["quote_bal"] = 0
        resampled_data["bal"] = 0

    return resampled_data


def _updateData():
    """
    Update ´DATA´ global

    Basically merge previous data with new data in files
    """

    global DATA

    if not os.path.isfile(conf.RESAMPLED_TRADES_FILE) \
       or not os.path.isfile(conf.INDICATORS_FILE):
        log.warning("Data files not found... Is it your first time around?")
        return False

    if lock.isLocked(conf.LOCAL_LOCK_FILE):
        # log.warning("graph._updateData(): won't update, lock file found")
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
    fresh_data.index = pd.to_datetime(fresh_data.index, unit="us")
    fresh_data = _resampleLedgerAndJoinTo(fresh_data)

    DATA = DATA.iloc[:-1].append(fresh_data).iloc[-conf.MAX_GRAPH_POINTS:]

    return True


def _initData():
    """
    Initialize ´DATA´ global

    Basically read ´conf.MAX_GRAPH_POINTS´ from data files
    """

    global DATA

    # init lock file
    while lock.isLocked(conf.LOCAL_LOCK_FILE):
        time.sleep(0.1)

    if not os.path.isfile(conf.RESAMPLED_TRADES_FILE) \
       or not os.path.isfile(conf.INDICATORS_FILE):
        log.warning("Data files not found... Is it your first time around?")
        DATA = pd.DataFrame(
            columns=conf.RESAMPLED_TRADES_COLUMNS
            + conf.INDICATORS_COLUMNS
            + conf.RESAMPLED_LEDGER_COLUMNS
            + ["bal"]  # hmmm... we'll calculate this on the fly:
        )
        return

    DATA = fu.getLastLines(
        conf.RESAMPLED_TRADES_FILE,
        conf.MAX_GRAPH_POINTS,
        conf.RESAMPLED_TRADES_COLUMNS
    )
    DATA = DATA.join(
        fu.getLastLines(
            conf.INDICATORS_FILE,
            conf.MAX_GRAPH_POINTS,
            conf.INDICATORS_COLUMNS
        )
    )
    DATA.index = pd.to_datetime(DATA.index, unit="us")
    DATA = _resampleLedgerAndJoinTo(DATA)


def _updateGraph(unused_counter, lines):
    """Function called (back) by FuncAnimation, will update graph"""

    if not _updateData():
        return lines.values()

    for key in lines:
        lines[key].set_data(DATA.index, DATA[key])
    return lines.values()


def _initGraph():
    """Wrapped to display errors (this is running in a separate process)"""

    _initData()

    fig = plt.figure()
    axes = {}
    axes["vwap"] = plt.subplot2grid((6, 1), (0, 0), rowspan=4)
    axes["volume"] = plt.subplot2grid((6, 1), (4, 0), sharex=axes["vwap"])
    axes["bal"] = plt.subplot2grid((6, 1), (5, 0), sharex=axes["vwap"])

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
        axes[key].legend(
            loc="upper left",
            prop={'size': 8},
            fancybox=True,
            framealpha=0.3
        )
        axes[key].yaxis.set_label_position("right")
        axes[key].yaxis.tick_right()

    plt.subplots_adjust(top=0.97, left=0.03, right=0.92, hspace=0.05)

    # the assignations are needed to avoid garbage collection...
    unused_animation = animation.FuncAnimation(  # NOQA: F841
        fig,
        _updateGraph,
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
        log.error("Something's bjorked in your graph :/")
