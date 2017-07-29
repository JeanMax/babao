"""Data visualisation inside"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import MultiCursor

MAX_POINTS = 42000  # TODO: move to config/arg
DATA = None


def initGraph(full_data):
    """TODO"""

    global DATA
    full_data.index = pd.to_datetime(full_data.index, unit="s")
    DATA = full_data

    fig = plt.figure()
    axes = {}
    axes["vwap"] = fig.add_subplot(2, 1, 1)
    axes["volume"] = fig.add_subplot(2, 1, 2, sharex=axes["vwap"])

    lines = {}
    lines["vwap"], = axes["vwap"].plot_date(
        DATA.index,
        DATA["vwap"],
        "-",
        label="vwap",
        color="b",
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
    #    axes["vwap"], DATA.values,
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

    plt.setp(axes["vwap"].get_xticklabels(), visible=False)
    for label in axes["volume"].xaxis.get_ticklabels():
        label.set_rotation(45)

    adf = axes["volume"].xaxis.get_major_formatter()
    adf.scaled[1./86400] = '%d/%m/%y %H:%M'
    adf.scaled[1./1440] = '%d/%m/%y %H:%M'
    adf.scaled[1./24] = '%d/%m/%y %H:%M'
    adf.scaled[1.] = '%d/%m/%y'
    adf.scaled[30.] = '%d/%m/%y'
    adf.scaled[365.] = '%d/%m/%y'

    axes["vwap"].set_ylabel("EUR")
    axes["volume"].set_ylabel("BTC")

    for key in axes:
        axes[key].grid(True)
        axes[key].legend(loc="upper left")
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
        fargs=(lines, axes),
        # blit=True,  # bug?
        interval=3000
    )

    plt.show()  # this is blocking!


def updateGraph(unused_counter, lines, unused_axes):
    """TODO"""
    # print(repr(DATA.head()))

    # line.set_data([1,2,3], [i,i,i])

    return lines.values()
