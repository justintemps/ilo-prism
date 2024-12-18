import pandas as pd
import numpy as np
from ._client import HuggingFaceClient
from tabulate import tabulate


class Summarizer(HuggingFaceClient):
    def __init__(self, model):
        super().__init__(model)

    def key_metrics(self, df: pd.DataFrame):
        start_period = df["TIME_PERIOD"].iloc[0]
        start_value = df["value"].iloc[0]
        end_period = df["TIME_PERIOD"].iloc[-1]
        end_value = df["value"].iloc[-1]
        max_year = df["TIME_PERIOD"].iloc[df["value"].idxmax()]
        max_value = df["value"].max()
        min_year = df["TIME_PERIOD"].iloc[df["value"].idxmin()]
        min_value = df["value"].min()
        range_value = max_value - min_value
        return {
            "start_period": start_period,
            "end_period": end_period,
            "start_value": start_value,
            "end_value": end_value,
            "max_year": max_year,
            "max_value": max_value,
            "min_year": min_year,
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
        Generate a concise summary of the following labour statistics retrieved from the International Labour Organization's ILOSTAT database, using a factual and objective tone. Focus strictly on patterns, trends, figures, and relationships evident in the data.

        **Context**:
        - Geographic Area: {area_label}
        - Dataset: {data_label}
        - Description: {data_description}

        **Key Metrics**:
        - Start: {key_metrics["start_period"]} = {key_metrics["start_value"]}
        - End: {key_metrics["end_period"]} = {key_metrics["end_value"]}
        - Peak: {key_metrics["max_year"]} = {key_metrics["max_value"]} (highest point)
        - Minimum: {key_metrics["min_year"]} = {key_metrics["min_value"]} (lowest point)

        **Observation**:
        {general_summary}

        **Instructions**:
        1. Summarize the general trend of the data in a paragraph.
        2. Focus on overall patterns, key increases or decreases, peaks, and minimums.
        3. Use clear and concise language suitable for a general audience.

        Your response should be coherent, factual, and easy to understand.
        """
        return prompt

    def respond(
        self, df: pd.DataFrame, area_label: str, data_label: str, data_description=str
    ):
        key_metrics = self.key_metrics(df)

        general_summary = self.general_summary(df, key_metrics)

        prompt = self.prompt(
            area_label, data_label, data_description, key_metrics, general_summary
        )

        response = self._client.summarization(text=prompt)

        return response.summary_text


if __name__ == "__main__":

    from app import SUMMARIZATION_MODEL

    summarizer = Summarizer(model=SUMMARIZATION_MODEL)

    data = {
        "Reference Area": {
            0: "World",
            1: "World",
            2: "World",
        },
        "Classification: SEX": {
            0: "Total",
            1: "Total",
            2: "Total",
        },
        "Classification: AGE": {
            0: "15+",
            1: "15+",
            2: "15+",
        },
        "TIME_PERIOD": {
            0: "1991",
            1: "1992",
            2: "1993",
        },
        "value": {
            0: 5.1,
            1: 5.3,
            2: 5.5,
        },
    }

    dataframe = pd.DataFrame.from_dict(data)

    key_metrics = summarizer.key_metrics(dataframe)

    general_summary = summarizer.general_summary(dataframe, key_metrics)

    print(key_metrics)
    print(general_summary)
