"""Data visualisation inside"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import dates as mdates
from matplotlib import ticker as mticker
# from matplotlib.widgets import Cursor

MAX_POINTS = 42000  # TODO: move to config/arg
DATA = None


def initGraph(full_data):
    """TODO"""

    global DATA
    full_data.index = pd.to_datetime(full_data.index, unit="s")
    DATA = full_data

    fig = plt.figure()
    ax1 = plt.subplot2grid((1, 1), (0, 0))
    ax1_bis = ax1.twinx()

    # ax1 = fig.add_subplot(2, 1, 1)
    # ax2 = fig.add_subplot(2, 1, 2, sharex=ax1)

    ln1, = ax1.plot_date(
        DATA.index,
        DATA["vwap"],
        "-",
        label="vwap",
        animated=True
    )

    ax1_bis.fill_between(
        DATA.index,
        0,
        DATA["volume"],
        label="volume",
        facecolor="g",
        alpha=0.4
    )

    # ax1.plot_date(DATA.index, DATA["vwap"], "-", label="vwap")
    # ax2.plot_date(DATA.index, DATA["volume"], "-", label="volume")

    # DATA["vwap"].plot(secondary_y=True, legend=True) #logy=True
    # DATA["volume"].plot(legend=True)

    # slow and ugly, plus there is something wrong with date format
    # candlestick_ohlc(
    #    ax1, DATA.values,
    #    width=0.05, colorup='g', colordown='r'
    # )

    # not so good when zooming in :/
    # ax1.annotate(
    #     str(int(DATA["vwap"][-1])),
    #     (DATA.index[-1], DATA["vwap"][-1]),
    #     xytext=(
    #         DATA.index[-1]
    #         + (DATA.index[-1] - DATA.index[-100]),
    #         DATA["vwap"][-1]
    #     ),
    #     bbox={"boxstyle":"larrow"}
    # )

    ax1.grid(True)
    ax1_bis.grid(False)

    h1, l1 = ax1.get_legend_handles_labels()
    h2, l2 = ax1_bis.get_legend_handles_labels()
    plt.legend(h1 + h2, l1 + l2, loc="upper left")

    for label in ax1.xaxis.get_ticklabels():
        label.set_rotation(45)
    # ax1.set_yticks(range(0, 4000, 100))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m/%y %H:%M"))
    ax1.xaxis.set_major_locator(mticker.MaxNLocator(14))
    # plt.xlabel("Date")

    ax1_bis.axes.yaxis.set_ticklabels([])
    ax1.set_ylabel("price")

    plt.subplots_adjust(top=0.95)

    # bugged since using animation (flash)
    # unused_cursor = Cursor(ax1_bis, useblit=True, color='black', linewidth=.5)

    # the assignation are needed to avoid garbage collection...
    unused_animation = animation.FuncAnimation(  # NOQA: F841
        fig,
        updateGraph,
        fargs=(ln1,),
        blit=True,
        interval=50
    )

    plt.show()  # this is blocking!


def updateGraph(unused_counter, line):
    """TODO"""
    # print(repr(DATA.head()))

    # line.set_data([1,2,3], [i,i,i])

    return line,
