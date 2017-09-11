"""Data visualisation inside"""

import os
import time
import traceback
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import MultiCursor

import babao.utils.date as du
import babao.utils.file as fu
import babao.utils.log as log
import babao.utils.lock as lock
import babao.config as conf
import babao.data.resample as resamp
import babao.data.indicators as indic

DATA = None
INDICATORS_COLUMNS = [
    "SMA_vwap_9", "SMA_vwap_26",
    "SMA_volume_9", "SMA_volume_26",
]
MAX_LOOK_BACK = 26


def _addIndicators(resampled_data):
    """TODO"""

    for indic_col in INDICATORS_COLUMNS:
        a = indic_col.split("_")
        fun, args = a[0], (resampled_data[a[1]], *tuple(a[2:]))
        resampled_data[indic_col] = getattr(indic, fun)(*args)

    return resampled_data


def _resampleLedgerAndJoinTo(resampled_data, since):
    """
    Resample ´conf.RAW_LEDGER_FILE´ and join it to ´resampled_data´

    Only entries included in ´resampled_data.index´ time window will be joined
    Return the result of this join
    """

    try:
        raw_ledger = fu.read(
            conf.DB_FILE,
            conf.LEDGER_FRAME,
            where="index > " + since
        )
        du.to_datetime(raw_ledger)
        for col in raw_ledger.columns:
            if col not in conf.RESAMPLED_LEDGER_COLUMNS:
                del raw_ledger[col]
        first = resampled_data.index[0]
        last = resampled_data.index[-1]
        resampled_ledger = raw_ledger.resample(
            # TODO: these are pasted from resample.py...
            str(conf.TIME_INTERVAL) + "Min",
            closed="right",
            label="right",
            base=(last.minute + (last.second + 1) / 60) % 60
        ).last()

        resampled_data = resampled_data.join(
            resampled_ledger,
            how="outer"
        ).ffill().fillna(0).loc[first:last]

        resampled_data["bal"] = resampled_data["quote_bal"] \
            + resampled_data["crypto_bal"] * resampled_data["vwap"]
    except (FileNotFoundError, KeyError):
        resampled_data["crypto_bal"] = 0
        resampled_data["quote_bal"] = 0
        resampled_data["bal"] = 0

    return resampled_data


def _getData(block=False):
    """
    Initialize ´DATA´ global

    Basically read ´conf.MAX_GRAPH_POINTS´ from data files
    """

    global DATA

    # init lock file
    while lock.isLocked(conf.LOCAL_LOCK_FILE):
        if block:
            time.sleep(0.1)
        else:
            # log.warning("graph._getData(): won't update, lock file found")
            return False

    if not os.path.isfile(conf.DB_FILE):
        log.warning("Data files not found... Is it your first time around?")
        DATA = pd.DataFrame(
            columns=conf.RESAMPLED_TRADES_COLUMNS
            + INDICATORS_COLUMNS
            + conf.RESAMPLED_LEDGER_COLUMNS
            + ["bal"]  # hmmm... we'll calculate this on the fly:
        )
        # TODO: catch missing frame errors
        return False

    since = str(
        fu.getLastRows(conf.DB_FILE, conf.TRADES_FRAME, 1).index[0]
        - ((MAX_LOOK_BACK + conf.MAX_GRAPH_POINTS) * 60 * 60 * 10**9)
    )
    DATA = fu.read(conf.DB_FILE, conf.TRADES_FRAME, where="index > " + since)
    DATA = resamp.resampleTradeData(DATA)
    DATA = _addIndicators(DATA).dropna()
    du.to_datetime(DATA)
    DATA = _resampleLedgerAndJoinTo(DATA, since)

    return True


def _updateGraph(unused_counter, lines):
    """Function called (back) by FuncAnimation, will update graph"""

    if not _getData(block=False):
        return lines.values()

    for key in lines:
        lines[key].set_data(DATA.index, DATA[key])
    return lines.values()


def _initGraph():
    """Wrapped to display errors (this is running in a separate process)"""

    _getData(block=True)

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
            for i, col in enumerate(INDICATORS_COLUMNS):
                if key in col:
                    lines[col], = axes[key].plot(
                        DATA.index,
                        DATA[col],
                        label=col.replace("_", " "),
                        color="r",
                        alpha=0.7 - 0.2 * (i % 2)
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
