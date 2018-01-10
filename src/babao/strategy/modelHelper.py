"""
The functions shared between the between the differents models are here

THey could be called from the models themselves, or from the modelManager
"""

import pandas as pd

import babao.utils.date as du

SCALE_MAX = 100000
SCALE_MIN = 0


def plotModel(model, full_data):
    """Plot the given model"""

    import matplotlib.pyplot as plt  # lazy load...

    y = unscale(model.FEATURES)  # be sure it has been scale_fit'ed
    # ndim should be 2/3, otherwise you deserve a crash
    if y.ndim == 3:  # keras formated
        y = y.reshape((y.shape[0], y.shape[2]))

    plot_data = pd.DataFrame(y).iloc[:, :len(model.REQUIRED_COLUMNS)]
    plot_data.columns = model.REQUIRED_COLUMNS
    plot_data.index = full_data.index[:len(y)]
    # TODO: these are not exactly the right indexes...

    plot_scale = plot_data["vwap"].max() * 2

    targets = model.getMergedTargets()
    if targets is not None:
        plot_data["y"] = targets * plot_scale * 0.8
        plot_data["y-sell"] = plot_data["y"].where(plot_data["y"] > 0)
        plot_data["y-buy"] = plot_data["y"].where(plot_data["y"] < 0) * -1

        plot_data["y-sell"].replace(0, plot_scale, inplace=True)
        plot_data["y-buy"].replace(0, plot_scale, inplace=True)

    plot_data["p"] = model.predict() * plot_scale
    plot_data["p-sell"] = plot_data["p"].where(plot_data["p"] > 0)
    plot_data["p-buy"] = plot_data["p"].where(plot_data["p"] < 0) * -1

    for col in plot_data.columns:
        if col not in ["vwap", "p-buy", "p-sell", "y-buy", "y-sell"]:
            del plot_data[col]
    du.to_datetime(plot_data)
    plot_data.fillna(0, inplace=True)

    plot_data.plot()
    plt.show(block=False)


def scale(arr):
    """Scale features before train/predict"""

    return (arr - SCALE_MIN) / (SCALE_MAX - SCALE_MIN)


def scale_fit(arr):
    """Init scaler, then scale features before train/predict"""

    global SCALE_MAX
    global SCALE_MIN
    SCALE_MAX = max(arr.max())  # this is a little optimistic about ´arr´ shape
    SCALE_MIN = min(arr.min())
    # TODO: use a different scale for volume?

    return scale(arr)


def unscale(arr):
    """Unscale features after train/predict"""

    return arr * (SCALE_MAX - SCALE_MIN) + SCALE_MIN
