"""Data visualisation inside"""

import sys
import os
import traceback
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import MultiCursor

import babao.utils.signal as sig
import babao.utils.date as du
import babao.utils.file as fu
import babao.utils.log as log
import babao.config as conf
import babao.utils.indicators as indic
import babao.models.tree.macdModel as macd  # TODO: this is weird
import babao.inputs.ledger.ledgerManager as lm
import babao.inputs.inputManager as im
from babao.utils.enum import CryptoEnum
from babao.inputs.trades.krakenTradesInput import KrakenTradesXXBTZEURInput

K = None
DATA = None
INDICATORS_COLUMNS = [
    "SMA_KrakenTradesXXBTZEURInput-vwap_9",
    "SMA_KrakenTradesXXBTZEURInput-vwap_26",
    "SMA_KrakenTradesXXBTZEURInput-vwap_77",
    "SMA_KrakenTradesXXBTZEURInput-volume_26",
    "SMA_KrakenTradesXXBTZEURInput-volume_77",
]  # TODO :o
MAX_LOOK_BACK = 77


def _getData():
    """
    Initialize ´DATA´ global

    Basically read ´conf.MAX_GRAPH_POINTS´ from data files
    """

    global DATA

    if not os.path.isfile(conf.DB_FILE):
        log.warning("Data files not found... Is it your first time around?")
        # TODO: catch missing frame errors
        return False

    since = K.last_row.name - du.secToNano(
        (MAX_LOOK_BACK + conf.MAX_GRAPH_POINTS) * 60 * 60
    )
    DATA = im.readInputs(
        [K, lm.LEDGERS[conf.QUOTE], lm.LEDGERS[CryptoEnum.XBT]],
        since
    )
    DATA = indic.get(DATA, INDICATORS_COLUMNS)
    DATA["macd_line"], DATA["signal_line"], DATA["macd"] = indic.MACD(
        DATA["KrakenTradesXXBTZEURInput-vwap"],
        macd.MODEL["a"], macd.MODEL["b"], macd.MODEL["c"], True
    )
    DATA = DATA.dropna()
    DATA["bal"] = DATA["FakeLedgerEURInput-balance"] \
        + DATA["FakeLedgerXBTInput-balance"] \
        * DATA["KrakenTradesXXBTZEURInput-close"]
    du.to_datetime(DATA)

    return True


def _updateGraph(unused_counter, lines):
    """Function called (back) by FuncAnimation, will update graph"""

    if sig.EXIT:
        sys.exit(0)
    if not _getData():
        return lines.values()

    for key in lines:
        lines[key].set_data(DATA.index, DATA[key])
    return lines.values()


def _initGraph():
    """Wrapped to display errors (this is running in a separate process)"""

    fig = plt.figure()
    axes = {}
    axes["KrakenTradesXXBTZEURInput-vwap"] = plt.subplot2grid(
        (8, 1), (0, 0), rowspan=5
    )
    axes["KrakenTradesXXBTZEURInput-volume"] = plt.subplot2grid(
        (8, 1), (5, 0), sharex=axes["KrakenTradesXXBTZEURInput-vwap"]
    )
    axes["macd"] = plt.subplot2grid(
        (8, 1), (6, 0), sharex=axes["KrakenTradesXXBTZEURInput-vwap"]
    )
    axes["bal"] = plt.subplot2grid(
        (8, 1), (7, 0), sharex=axes["KrakenTradesXXBTZEURInput-vwap"]
    )

    lines = {}
    for key in axes:  # TODO: this is *really* ugly
        lines[key], = axes[key].plot(
            DATA.index,
            DATA[key],
            # "-+",
            label=key,
            color="b",
            alpha=0.5
        )
        plt.setp(axes[key].get_xticklabels(), visible=False)
        if key == "bal":
            col = "FakeLedgerEURInput-balance"
            lines[col], = axes[key].plot(
                DATA.index,
                DATA[col],
                label=col.replace("_", " "),
                color="r",
                alpha=0.5
            )
        elif key == "macd":
            for i, col in enumerate(["macd_line", "signal_line"]):
                lines[col], = axes[key].plot(
                    DATA.index,
                    DATA[col],
                    label=col.replace("_", " "),
                    color="r",
                    alpha=0.7 - 0.2 * (i % 3)
                )
        else:  # add indicators to vol/vwap
            for i, col in enumerate(INDICATORS_COLUMNS):
                if key in col:
                    lines[col], = axes[key].plot(
                        DATA.index,
                        DATA[col],
                        label=col.replace("_" + key, "").replace("_", " "),
                        color="r",
                        alpha=0.7 - 0.2 * (i % 3)
                    )
        if key == "KrakenTradesXXBTZEURInput-vwap":
            col = "KrakenTradesXXBTZEURInput-close"
            lines[col], = axes[key].plot(
                DATA.index,
                DATA[col],
                label=col,
                color="g",
                alpha=0.5
            )

    # the assignation is needed to avoid garbage collection...
    unused_cursor = MultiCursor(  # NOQA: F841
        fig.canvas,
        list(axes.values()),
        useblit=True,
        color="black",
        lw=0.5,
        horizOn=True
    )  # TODO: redraw me!

    plt.setp(axes["bal"].get_xticklabels(), visible=True)
    for label in axes["bal"].xaxis.get_ticklabels():
        label.set_rotation(45)
    adf = axes["bal"].xaxis.get_major_formatter()
    adf.scaled[1. / 86400] = "%d/%m/%y %H:%M"
    adf.scaled[1. / 1440] = "%d/%m/%y %H:%M"
    adf.scaled[1. / 24] = "%d/%m/%y %H:%M"
    adf.scaled[1.] = "%d/%m/%y"
    adf.scaled[30.] = "%d/%m/%y"
    adf.scaled[365.] = "%d/%m/%y"

    y_min = DATA["KrakenTradesXXBTZEURInput-vwap"].min()
    y_max = DATA["KrakenTradesXXBTZEURInput-vwap"].max()
    space = (y_max - y_min) * 0.05  # 5% space up and down
    axes["KrakenTradesXXBTZEURInput-vwap"].set_ylim(
        bottom=y_min - space, top=y_max + space
    )
    axes["KrakenTradesXXBTZEURInput-volume"].set_ylim(bottom=0)
    y_max = max(DATA["macd"].max(), DATA["macd"].min() * -1)
    axes["macd"].set_ylim(bottom=-y_max, top=y_max)
    axes["bal"].set_ylim(bottom=0, top=200)

    axes["KrakenTradesXXBTZEURInput-vwap"].set_ylabel("XBT")
    axes["KrakenTradesXXBTZEURInput-volume"].set_ylabel("EUR")
    axes["macd"].set_ylabel("%")
    axes["bal"].set_ylabel("XBT")

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

        # # not so good when zooming in :/
        # last_x = DATA.index[-1]
        # last_y = DATA[key].iloc[-1]
        # axes[key].annotate(
        #     str(int(last_y)),
        #     (last_x, last_y),
        #     xytext=(
        #         last_x + (last_x - DATA.index[-21]),
        #         last_y
        #     ),
        #     bbox={"boxstyle": "larrow"}
        # )  # TODO: save this, then give it to the update fun

    plt.subplots_adjust(top=0.97, left=0.03, right=0.92, hspace=0.05)

    # the assignations are needed to avoid garbage collection...
    unused_animation = animation.FuncAnimation(  # NOQA: F841
        fig,
        _updateGraph,
        fargs=(lines,),
        # blit=True,  # bug?
        interval=3000
    )
    plt.show()  # this is blocking!


def initGraph(log_lock, file_lock):
    """Launch an awesome matplotlib graph!"""

    log.setLock(log_lock)
    fu.setLock(file_lock)
    global K
    K = KrakenTradesXXBTZEURInput()
    fu.closeStore()
    sig.catchSignal()
    try:
        _getData()
        _initGraph()
    except:  # pylint: disable=bare-except
        traceback.print_exc()
        log.error("Something's bjorked in your graph :/")
    sys.exit(0)  # we exit explicitly in the subprocess, to avoid double clean
