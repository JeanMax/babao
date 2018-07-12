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
        self.scale_min = arr.min()
        self.scale_max = arr.max()
        if len(arr.shape) > 1:
            self.scale_min = min(self.scale_min)
            self.scale_max = max(self.scale_max)

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

    def scaleFit(self, arr):
        """Scale n Fit"""
        self.fit(arr)
        return self.scale(arr)
