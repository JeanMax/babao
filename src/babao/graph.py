"""Data visualisation inside"""

import sys
import os
import traceback
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import MultiCursor

import babao.utils.date as du
import babao.utils.log as log
import babao.config as conf
import babao.utils.indicators as indic
import babao.strategy.models.macd as macd  # TODO: this is weird
import babao.strategy.transaction as tx
from babao.inputs.inputBase import ABCInput
from babao.inputs.trades.krakenTradesInput import KrakenTradesXXBTZEURInput
from babao.inputs.trades.tradesInputBase import ABCTradesInput

K = None
DATA = None
INDICATORS_COLUMNS = [
    "SMA_vwap_9", "SMA_vwap_26", "SMA_vwap_77",
    "SMA_volume_26", "SMA_volume_77",
]
MAX_LOOK_BACK = 77


def _resampleLedgerAndJoinTo(resampled_data, since):
    """
    Resample ´conf.RAW_LEDGER_FILE´ and join it to ´resampled_data´

    Only entries included in ´resampled_data.index´ time window will be joined
    Return the result of this join
    """

    try:
        crypto_ledger = tx.L["crypto"].resample(tx.L["crypto"].read(since))
        quote_ledger = tx.L["quote"].resample(tx.L["quote"].read(since))
        du.to_datetime(crypto_ledger)
        du.to_datetime(quote_ledger)

        if not crypto_ledger.empty:
            resampled_data["crypto_bal"] = crypto_ledger["balance"]
        else:
            resampled_data["crypto_bal"] = 0
        if not quote_ledger.empty:
            resampled_data["quote_bal"] = quote_ledger["balance"]
        else:
            resampled_data["quote_bal"] = 0

        # resampled_data = resampled_data.join(
        #     crypto_ledger, how="outer"
        # ).join(
        #     quote_ledger, how="outer"
        # )
        first = resampled_data.index[0]
        last = resampled_data.index[-1]
        resampled_data = resampled_data.ffill().fillna(0).loc[first:last]

        resampled_data["bal"] = resampled_data["quote_bal"] \
            + resampled_data["crypto_bal"] * resampled_data["close"]
    except (FileNotFoundError, KeyError, OSError) as e:
        if e == OSError:
            log.warning(repr(e))
        resampled_data["crypto_bal"] = 0
        resampled_data["quote_bal"] = 0
        resampled_data["bal"] = 0

    return resampled_data


def _getData():
    """
    Initialize ´DATA´ global

    Basically read ´conf.MAX_GRAPH_POINTS´ from data files
    """

    global DATA

    if not os.path.isfile(conf.DB_FILE):
        log.warning("Data files not found... Is it your first time around?")
        DATA = pd.DataFrame(
            columns=ABCTradesInput.resampled_columns
            + INDICATORS_COLUMNS
            + ["crypto_bal", "quote_bal", "bal"]
            # hmmm... we'll calculate these on the fly
            + ["macd_line", "signal_line", "macd"]  # these too :O
        )
        # TODO: catch missing frame errors
        return False

    since = K.last_row.name - (
        (MAX_LOOK_BACK + conf.MAX_GRAPH_POINTS) * 60 * 60 * 10**9
    )
    DATA = K.read(since)
    DATA = K.resample(DATA)
    DATA = indic.get(DATA, INDICATORS_COLUMNS).dropna()
    DATA["macd_line"], DATA["signal_line"], DATA["macd"] = indic.MACD(
        DATA["vwap"], macd.MODEL["a"], macd.MODEL["b"], macd.MODEL["c"], True
    )
    du.to_datetime(DATA)
    DATA = _resampleLedgerAndJoinTo(DATA, since)

    return True


def _updateGraph(unused_counter, lines):
    """Function called (back) by FuncAnimation, will update graph"""

    if not _getData():
        return lines.values()

    for key in lines:
        lines[key].set_data(DATA.index, DATA[key])
    return lines.values()


def _initGraph():
    """Wrapped to display errors (this is running in a separate process)"""

    _getData()

    fig = plt.figure()
    axes = {}
    axes["vwap"] = plt.subplot2grid((8, 1), (0, 0), rowspan=5)
    axes["volume"] = plt.subplot2grid((8, 1), (5, 0), sharex=axes["vwap"])
    axes["macd"] = plt.subplot2grid((8, 1), (6, 0), sharex=axes["vwap"])
    axes["bal"] = plt.subplot2grid((8, 1), (7, 0), sharex=axes["vwap"])

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
            col = "quote_bal"
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

    y_min = DATA["vwap"].min()
    y_max = DATA["vwap"].max()
    space = (y_max - y_min) * 0.05  # 5% space up and down
    axes["vwap"].set_ylim(bottom=y_min - space, top=y_max + space)
    axes["volume"].set_ylim(bottom=0)
    y_max = max(DATA["macd"].max(), DATA["macd"].min() * -1)
    axes["macd"].set_ylim(bottom=-y_max, top=y_max)
    axes["bal"].set_ylim(bottom=0, top=200)

    axes["vwap"].set_ylabel(conf.ASSET_PAIR[4:])
    axes["volume"].set_ylabel(conf.ASSET_PAIR[:4])
    axes["macd"].set_ylabel("%")
    axes["bal"].set_ylabel(conf.ASSET_PAIR[4:])

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


def initGraph(log_lock, rw_lock):
    """Launch an awesome matplotlib graph!"""

    global K
    K = KrakenTradesXXBTZEURInput()
    log.setLock(log_lock)
    ABCInput.rw_lock = rw_lock
    try:
        _initGraph()
    except:  # pylint: disable=bare-except
        traceback.print_exc()
        log.error("Something's bjorked in your graph :/")
    sys.exit(0)  # we exit explicitly in the subprocess, to avoid double clean
