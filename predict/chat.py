import pandas as pd
from ._client import HuggingFaceClient
import numpy as np


class ChatBot(HuggingFaceClient):
    def __init__(self, model):
        super().__init__(model)

        self.MAX_TOKENS = 1000

        self.TEMPERATURE = 1

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
        self,
        df: pd.DataFrame,
        area_label: str,
        data_label: str,
        data_description=str,
    ):
        # Initialize the messages with the first system message
        messages = [{"role": "system", "content": "You are a helpful chatbot"}]

        key_metrics = self.key_metrics(df)

        general_summary = self.general_summary(df, key_metrics)

        prompt = self.prompt(
            area_label, data_label, data_description, key_metrics, general_summary
        )

        # Adds the current message from the user
        messages.append({"role": "user", "content": prompt})

        # Initialize the response
        response = ""

        # Pass the current message to the client and ask for completion together with the params
        # that we add in the Interface
        for msg in self._client.chat_completion(
            messages=messages,
            max_tokens=self.MAX_TOKENS,
            temperature=self.TEMPERATURE,
            stream=True,
        ):
            # The current token
            token = msg.choices[0].delta.content

            # The response from the current foken
            response += token

            # Yield the next part of the response
            yield response
