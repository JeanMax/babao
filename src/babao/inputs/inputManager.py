"""
TODO
or is it a manager?
"""

from functools import partial


def readInputs(input_list, since=None):
    """TODO"""

    def _renamer(prefix, s):
        """TODO"""
        return prefix + "-" + s

    def _restorer(prefix, s):
        """TODO"""
        return s.replace(prefix + "-", "")

    # TODO: opt memory usage / lock once
    data_list = [inp.read(since) for inp in input_list]

    # TODO: ensure resample base is correct (use till, or?)
    for i, inp in enumerate(input_list):
        data_list[i] = inp.resample(data_list[i])
        partial_renamer = partial(_renamer, inp.__class__.__name__)
        data_list[i].rename(partial_renamer, axis="columns", inplace=True)

    df = data_list[0].join(data_list[1:], how="outer")

    for inp in input_list:
        partial_restorer = partial(_restorer, inp.__class__.__name__)
        partial_renamer = partial(_renamer, inp.__class__.__name__)
        inp_col = [partial_renamer(col) for col in inp.resampled_columns]
        df[inp_col] = inp.fillMissing(
            df.loc[:, inp_col].rename(partial_restorer, axis="columns")
        )

    return df
