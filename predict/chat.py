import pandas as pd
from ._client import HuggingFaceClient
from ._descriptor import DataDescriptor
import numpy as np


class ChatBot(HuggingFaceClient):
    def __init__(self, model):
        super().__init__(model)

        self.MAX_TOKENS = 1000

        self.TEMPERATURE = 0.7

    def print_metrics(self, data: DataDescriptor) -> str:
        df = data.milestones

        # Find start and end points
        start = f"Start: {data.start.time} = {data.start.value}"
        end = f"End: {data.end.time} = {data.end.value}"

        # Track inflection points (increases and decreases)
        summary_lines = []

        for i in range(1, len(df)):
            previous_value = df["value"].iloc[i - 1]
            current_value = df["value"].iloc[i]
            year = df["TIME_PERIOD"].iloc[i]

            if current_value > previous_value:
                summary_lines.append(f"Increase: {year} = {current_value}")
            elif current_value < previous_value:
                summary_lines.append(f"Decrease: {year} = {current_value}")

        # Mark highest and lowest points
        for i, line in enumerate(summary_lines):
            if str(data.max.value) in line:
                summary_lines[i] += " (Highest value)"
            if str(data.min.value) in line:
                summary_lines[i] += " (Lowest value)"

        # Combine all parts
        return "\n".join([start] + summary_lines + [end])

    def print_projections(self, data: DataDescriptor) -> str:
        projections_df = data.projections

        if projections_df.empty:
            return "No projections available."

        # Determine change type (Increase, Decrease, No change)
        def determine_change(current, previous):
            if current > previous:
                return "Increase"
            elif current < previous:
                return "Decrease"
            else:
                return "No change"

        # Initialize result lines
        result_lines = []

        # Get the last milestone value for comparison with the first projection
        last_milestone_value = data.milestones["value"].iloc[-1]
        first_projection_value = projections_df["value"].iloc[0]
        initial_change = determine_change(first_projection_value, last_milestone_value)

        # Add the first line
        result_lines.append(
            f"Projection: {projections_df['TIME_PERIOD'].iloc[0]} = {first_projection_value} ({initial_change})"
        )

        # Process subsequent projections
        for i in range(1, len(projections_df)):
            current_value = projections_df["value"].iloc[i]
            previous_value = projections_df["value"].iloc[i - 1]
            year = projections_df["TIME_PERIOD"].iloc[i]
            change = determine_change(current_value, previous_value)

            result_lines.append(f"Projection: {year} = {current_value} ({change})")

        return "\n".join(result_lines)

    def prompt(self, df, area_label: str, data_label: str):
        """
        Generate a prompt for summarizing labour statistics from a dataframe.

        Args:
            df: DataFrame containing labour statistics.
            area_label: Geographic area label.
            data_label: Dataset label.

        Returns:
            str: A formatted prompt string.
        """
        # Extract key insights from the data
        data = DataDescriptor(df)

        # Initialize the prompt with context and key metrics
        prompt = f"""Generate a concise summary of the following labour statistics from the International Labour Organization using a factual and objective tone.

**Context**
- Geographic Area: {area_label}
- Dataset: {data_label}
- Reference Year: {data.current_year}
"""

        # Append key metrics
        prompt += f"""
**Key Metrics**
{self.print_metrics(data)}
{self.print_projections(data)}
"""

        # Append observation and instructions
        prompt += f"""

**Observation**
- {data.trend}

**Instructions**
1. Summarize the general trend of the data in a single paragraph of four or five sentences.
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

            # The response from the current token
            response += token

            # Yield the next part of the response
            yield response


if __name__ == "__main__":
    from app.defaults import AppDefaults

    initial = AppDefaults()

    data = DataDescriptor(df=initial.dataframe)

    print(ChatBot.print_metrics(data))
    print(ChatBot.print_projections(data))
