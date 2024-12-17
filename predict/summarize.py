import pandas as pd
import numpy as np
from ._client import HuggingFaceClient
from tabulate import tabulate


class Summarizer(HuggingFaceClient):
    def __init__(self, model):
        super().__init__(model)

    def key_metrics(self, df: pd.DataFrame):
        start_value = df["value"].iloc[0]
        end_value = df["value"].iloc[-1]
        max_value = df["value"].max()
        min_value = df["value"].min()
        range_value = max_value - min_value
        return {
            "start_value": start_value,
            "end_value": end_value,
            "max_value": max_value,
            "min_value": min_value,
            "range_value": range_value,
        }

    def general_summary(self, df: pd.DataFrame, key_metrics: dict):
        start_value = key_metrics["start_value"]
        end_value = key_metrics["end_value"]
        range_value = key_metrics["range_value"]

        direction_changes = np.sign(df["value"].diff()).diff().fillna(0).abs().sum()
        # Analyze general trend
        if (
            direction_changes > len(df) * 0.3
        ):  # More than 30% changes imply fluctuations
            trend = "The values fluctuate significantly over time."
        elif start_value < end_value:
            trend = "The values show an overall upward trend."
        elif start_value > end_value:
            trend = "The values show an overall downward trend."
        elif range_value < 0.1:  # Small range implies stability
            trend = "The values remain relatively stable over time."
        else:
            trend = "The values show moderate variations over time."
        return trend

    def prompt(
        self,
        area_label: str,
        data_label: str,
        data_description: str,
        key_metrics: dict,
        general_summary: str,
    ):
        # Construct Prompt for LLM
        prompt = f"""
        You are tasked with summarizing the following time series data for a human reader.

        **Context**:
        - Area: {area_label}
        - Indicator: {data_label}
        - Description: {data_description}

        **Key Metrics**:
        - Start: {key_metrics["start_year"]} = {key_metrics["start_value"]}
        - End: {key_metrics["end_year"]} = {key_metrics["end_value"]}
        - Peak: {key_metrics["max_year"]} = {key_metrics["max_value"]} (highest point)
        - Minimum: {key_metrics["min_year"]} = {key_metrics["min_value"]} (lowest point)

        **Observation**:
        {general_summary}

        **Instructions**:
        1. Summarize the general trend of the data in 2-3 sentences.
        2. Focus on overall patterns, key increases or decreases, peaks, and minimums.
        3. Use clear and concise language suitable for a general audience.

        Your response should be coherent, factual, and easy to understand.
        """
        return prompt

    def respond(
        self, df: pd.DataFrame, area_label: str, data_label: str, data_description=str
    ):
        key_metrics = self.key_metrics(df)

        # general_summary = self.general_summary(df, key_metrics)
        print(key_metrics)
