"""Data visualisation inside"""

import os
import sys
import re
from functools import partial
# import traceback

import matplotlib.animation as animation
import matplotlib.pyplot as plt
from matplotlib.widgets import MultiCursor, Button

import babao.config as conf
import babao.inputs.inputManager as im
import babao.inputs.ledger.ledgerManager as lm
import babao.utils.date as du
import babao.utils.file as fu
import babao.utils.indicators as indic
import babao.utils.log as log
import babao.utils.signal as sig

INDEX = None
DATA = None
INDICATORS_COLUMNS = [
    "sma_vwap_9",
    "sma_vwap_26",
    "sma_vwap_77",
    "sma_volume_26",
    "sma_volume_77",
]
MAX_LOOK_BACK = 77


class Index():
    """Class keeping track of the current crypto to display"""
    def __init__(self, axes):
        self.axes = axes
        self.ind = 0
        self._update()

    def next(self, unused_event):
        """Show the next crypto"""
        self.ind = (self.ind + 1) % len(conf.CRYPTOS)
        self._update()

    def prev(self, unused_event):
        """Show the previous crypto"""
        self.ind = (self.ind - 1) % len(conf.CRYPTOS)
        self._update()

    def _update(self):
        """Update graph data and zoom after a next/prev click"""
        _getData()
        self.axes["vwap"].set_title(conf.CRYPTOS[self.ind].name)
        y_min = DATA["vwap"].min()
        y_max = DATA["vwap"].max()
        space = (y_max - y_min) * 0.05  # 5% space up and down
        self.axes["vwap"].set_ylim(
            bottom=y_min - space, top=y_max + space
        )
        y_max = DATA["volume"].max()
        space = y_max * 0.05
        self.axes["volume"].set_ylim(bottom=0, top=y_max - space)
        y_max = max(DATA["signal_line"].max(), DATA["signal_line"].min() * -1)
        self.axes["macd"].set_ylim(bottom=-y_max, top=y_max)
        self.axes["total-balance"].set_ylim(bottom=0, top=200)
        plt.draw()


def _getData():
    """
    Initialize ´DATA´ global

    Basically read ´conf.MAX_GRAPH_POINTS´ from data files
    """

    global DATA

    if not os.path.isfile(conf.DB_FILE):
        log.warning("Data files not found... Is it your first time around?")
        return False

    if INDEX is None:
        crypto = conf.CRYPTOS[0]
    else:
        crypto = conf.CRYPTOS[INDEX.ind]

    inputs = [
        lm.TRADES[crypto],
        lm.LEDGERS[conf.QUOTE],
        lm.LEDGERS[crypto]
    ]
    im.refreshInputs(inputs)
    since = lm.TRADES[crypto].current_row.name - du.secToNano(
        (MAX_LOOK_BACK + conf.MAX_GRAPH_POINTS) * conf.TIME_INTERVAL * 60
    )
    DATA = im.readInputs(inputs, since)

    DATA.rename(
        partial(re.sub, r'.*Trades.*-', ""),
        axis="columns", inplace=True
    )
    DATA.rename(
        partial(re.sub, r'.*Ledger' + conf.QUOTE.name + '.*-', "quote-"),
        axis="columns", inplace=True
    )
    DATA.rename(
        partial(re.sub, r'.*Ledger.*-', "crypto-"),
        axis="columns", inplace=True
    )
    DATA = DATA.loc[
        :,
        ['close', 'vwap', 'volume', 'quote-balance', 'crypto-balance']
    ]

    DATA = indic.get(DATA, INDICATORS_COLUMNS)
    DATA["macd_line"], DATA["signal_line"], DATA["macd"] = indic.macd(
        DATA["vwap"],
        46, 75, 22,
        True
    )
    DATA = DATA.dropna()
    DATA["total-balance"] = DATA["quote-balance"] \
        + DATA["crypto-balance"] * DATA["close"]
    du.toDatetime(DATA)

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


def _createAxes():
    """Create the different axes we'll need to draw in"""
    axes = {}
    axes["vwap"] = plt.subplot2grid(
        (8, 1), (0, 0), rowspan=5
    )
    axes["volume"] = plt.subplot2grid(
        (8, 1), (5, 0), sharex=axes["vwap"]
    )
    axes["macd"] = plt.subplot2grid(
        (8, 1), (6, 0), sharex=axes["vwap"]
    )
    axes["total-balance"] = plt.subplot2grid(
        (8, 1), (7, 0), sharex=axes["vwap"]
    )
    return axes


def _createLines(axes):
    """Draw desired lines with matplotlib"""
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
        if key == "total-balance":
            col = "quote-balance"
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
        if key == "vwap":
            col = "close"
            lines[col], = axes[key].plot(
                DATA.index,
                DATA[col],
                label=col,
                color="g",
                alpha=0.5
            )
    return lines


def _initGraph():
    """Wrapped to display errors (this is running in a separate process)"""

    fig = plt.figure()
    axes = _createAxes()
    lines = _createLines(axes)

    # the assignation is needed to avoid garbage collection...
    unused_cursor = MultiCursor(  # NOQA: F841
        fig.canvas,
        list(axes.values()),
        useblit=True,
        color="black",
        lw=0.5,
        horizOn=True
    )  # TODO: redraw me!

    plt.setp(axes["total-balance"].get_xticklabels(), visible=True)
    for label in axes["total-balance"].xaxis.get_ticklabels():
        label.set_rotation(45)
    adf = axes["total-balance"].xaxis.get_major_formatter()
    adf.scaled[1. / 86400] = "%d/%m/%y %H:%M"
    adf.scaled[1. / 1440] = "%d/%m/%y %H:%M"
    adf.scaled[1. / 24] = "%d/%m/%y %H:%M"
    adf.scaled[1.] = "%d/%m/%y"
    adf.scaled[30.] = "%d/%m/%y"
    adf.scaled[365.] = "%d/%m/%y"

    axes["vwap"].set_ylabel("PRICE")
    axes["volume"].set_ylabel("VOL")
    axes["macd"].set_ylabel("MACD")
    axes["total-balance"].set_ylabel("BAL")

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

    global INDEX
    INDEX = Index(axes)
    axprev = plt.axes([0.13, 0.974, 0.1, 0.025])
    axnext = plt.axes([0.75, 0.974, 0.1, 0.025])
    bnext = Button(axnext, 'next', color='0.5', hovercolor='0.9')
    bprev = Button(axprev, 'prev', color='0.5', hovercolor='0.9')
    bnext.on_clicked(INDEX.next)
    bprev.on_clicked(INDEX.prev)

    # the assignations are needed to avoid garbage collection...
    unused_animation = animation.FuncAnimation(  # NOQA: F841
        fig,
        _updateGraph,
        fargs=(lines,),
        # blit=True,  # bug?
        interval=5000
    )
    plt.show()  # this is blocking!


def initGraph(log_lock, file_lock):
    """Launch an awesome matplotlib graph!"""

    log.setLock(log_lock)
    fu.setLock(file_lock)
    sig.catchSignal()
    try:
        _getData()
        _initGraph()
    except Exception as e:
        log.warning("Something's bjorked in your graph :/")
        log.info("Try to run babao again with the env variable DEBUG_GRAPH set")
        # traceback.print_exc()
        raise e
    sys.exit(0)  # we exit explicitly in the subprocess, to avoid double clean
