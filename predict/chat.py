import pandas as pd
from ._client import HuggingFaceClient
import numpy as np
from datetime import datetime


class ChatBot(HuggingFaceClient):
    def __init__(self, model):
        super().__init__(model)

        self.MAX_TOKENS = 1000

        self.TEMPERATURE = 0.7

    def _key_metrics(self, df: pd.DataFrame):
        current_year = datetime.now().year

        # Convert TIME_PERIOD to numerical values for comparison
        df["TIME_PERIOD"] = pd.to_numeric(df["TIME_PERIOD"], errors="coerce")

        # Find the latest year on or before the current year
        valid_years = df[df["TIME_PERIOD"] <= current_year]
        if not valid_years.empty:
            end_period = valid_years["TIME_PERIOD"].iloc[-1]
            end_value = valid_years["value"].iloc[-1]
        else:
            end_period = None
            end_value = None

        # Extract data for years after the current year
        future_years = df[df["TIME_PERIOD"] > current_year]
        future_data = list(zip(future_years["TIME_PERIOD"], future_years["value"]))

        start_period = df["TIME_PERIOD"].iloc[0]
        start_value = df["value"].iloc[0]
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
            "future_data": future_data,
        }

    def _general_summary(self, df: pd.DataFrame, key_metrics: dict):
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
        df,
        area_label: str,
        data_label: str,
    ):
        # Get the key metrics from the dataframe
        key_metrics = self._key_metrics(df)

        # Create a general summary about the dataframe
        general_summary = self._general_summary(df, key_metrics)

        # Construct Prompt for LLM
        prompt = f"""Generate a concise summary of the following labour statistics using a factual and objective tone. Focus only on describing the statistical trend in the data without trying to explain why it changed over time.

        **Context**
        - Geographic Area: {area_label}
        - Dataset: {data_label}

        **Key Metrics**
        - Start: {key_metrics["start_period"]} = {key_metrics["start_value"]}
        - Peak: {key_metrics["max_year"]} = {key_metrics["max_value"]} (highest point)
        - Minimum: {key_metrics["min_year"]} = {key_metrics["min_value"]} (lowest point)
        - End: {key_metrics["end_period"]} = {key_metrics["end_value"]}
        """

        # Add projections if future data exists
        if key_metrics["future_data"]:
            prompt += "\n"
            prompt += f"   **Future Projections**"
            prompt += "\n"
            for year, value in key_metrics["future_data"]:
                trend = "increase" if value > key_metrics["end_value"] else "decrease"
                prompt += f"- {year} = {value} ({trend})\n"

        prompt += f"""
        **Observation**:
        - {general_summary}

        **Instructions**
        1. Summarize the general trend of the data in a paragraph.
        2. Focus on overall patterns, key increases or decreases, peaks, and minimums.
        3. Use clear and concise language suitable for a general audience.

        Your response should be coherent, factual, and easy to understand.
        """
        return prompt

    def respond(self, prompt: str):
        # Initialize the messages with the first system message
        messages = [{"role": "system", "content": "You are a helpful chatbot"}]

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
