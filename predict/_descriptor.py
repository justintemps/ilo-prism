import pandas as pd
import numpy as np
from datetime import datetime

"""
@TODO: The next step is to replace key metrics the way we have it now with a blow by blow. Basically we'll use find_peaks from scipy.signal to identify both the peaks and the valleys. We'll then put them in order to tell a story like the one we have in prompt.

peaks, _ = find_peaks(df['y_smooth'])
valleys, _ = find_peaks(-df['y_smooth'])  # Invert data for valleys

This should be added to DataDescriptor, not ChatBot.
"""


class TimeValue:
    def __init__(self, time: int, value: float, change: str = None):
        self.time = time
        self.value = value
        self.change = change


class DataDescriptor:
    def __init__(self, df: pd.DataFrame):
        self._df = df
        self.current_year = datetime.now().year

        # Convert TIME_PERIOD to numerical values for comparison
        self._df["TIME_PERIOD"] = pd.to_numeric(df["TIME_PERIOD"], errors="coerce")

        # Separate past years from projections
        self.past_years = df[df["TIME_PERIOD"] <= self.current_year]
        self.future_years = df[df["TIME_PERIOD"] > self.current_year]

        # Get the start period of the past years
        self.start = TimeValue(
            time=self.past_years["TIME_PERIOD"].iloc[0],
            value=self.past_years["value"].iloc[0],
        )

        # Get the end period of the past years (up to the present)
        self.end = TimeValue(
            time=self.past_years["TIME_PERIOD"].iloc[-1],
            value=self.past_years["value"].iloc[-1],
        )

        # Get the max value from the past years
        self.max = TimeValue(
            time=self.past_years["TIME_PERIOD"].iloc[self.past_years["value"].idxmax()],
            value=self.past_years["value"].max(),
        )

        # Get the min value from the past years
        self.min = TimeValue(
            time=self.past_years["TIME_PERIOD"].iloc[self.past_years["value"].idxmin()],
            value=self.past_years["value"].min(),
        )

    @property
    def range(self):
        return self.max.value - self.min.value

    @property
    def summary(self):
        direction_changes = (
            np.sign(self._df["value"].diff()).diff().fillna(0).abs().sum()
        )
        # Analyze general trend
        if (
            direction_changes > len(self._df) * 0.3
        ):  # More than 30% changes imply fluctuations
            trend = "The values fluctuate significantly over time."
        elif self.start.value < self.end.value:
            trend = "The values show an overall upward trend."
        elif self.start.value > self.end.value:
            trend = "The values show an overall downward trend."
        elif self.range < 0.1:  # Small range implies stability
            trend = "The values remain relatively stable over time."
        else:
            trend = "The values show moderate variations over time."
        return trend

    @property
    def projections(self):
        if self.future_years is None or self.future_years.empty:
            return None
        return [
            TimeValue(time=row["TIME_PERIOD"], value=row["value"])
            for _, row in self.future_years.iterrows()
        ]
