"""
TODO
"""


class Scaler:
    """TODO"""
    def __init__(self):
        self.scale_min = 0
        self.scale_max = 100000

    def fit(self, arr):
        """Init scaler"""
        # TODO: use a different scale for volume?
        self.scale_min = min(arr.min())
        self.scale_max = max(arr.max())
        # this is a little optimistic about ´arr´ shape

    def scale(self, arr):
        """Scale features before train/predict"""
        return (
            (arr - self.scale_min)
            / (self.scale_max - self.scale_min)
        )

    def unscale(self, arr):
        """Unscale features after train/predict"""
        return (
            arr * (self.scale_max - self.scale_min)
            + self.scale_min
        )

    def scale_fit(self, arr):
        """Scale n Fit"""
        self.fit(arr)
        return self.scale(arr)
