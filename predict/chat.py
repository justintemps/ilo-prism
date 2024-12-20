import pandas as pd
from ._client import HuggingFaceClient
from ._descriptor import DataDescriptor
import numpy as np
from scipy.signal import find_peaks

"""
@TODO: The next step is to replace key metrics the way we have it now with a blow by blow. Basically we'll use find_peaks from scipy.signal to identify both the peaks and the valleys. We'll then put them in order to tell a story like the one we have in prompt.

peaks, _ = find_peaks(df['y_smooth'])
valleys, _ = find_peaks(-df['y_smooth'])  # Invert data for valleys

This should be added to DataDescriptor, not ChatBot.
"""


class ChatBot(HuggingFaceClient):
    def __init__(self, model):
        super().__init__(model)

        self.MAX_TOKENS = 1000

        self.TEMPERATURE = 0.7

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

**Key Metrics**
- Start: {data.start.time} = {data.start.value}
- Peak: {data.max.time} = {data.max.value} (highest point)
- Minimum: {data.min.time} = {data.min.value} (lowest point)
- End: {data.end.time} = {data.end.value}
"""

        # Add projections to Key Metrics if available
        if data.projections:
            projections = "\n".join(
                f"- Projection: {projection.time} = {projection.value} ("
                + (
                    "increase"
                    if projection.value > data.end.value
                    else (
                        "decrease" if projection.value < data.end.value else "No change"
                    )
                )
                + ")"
                for projection in data.projections
            )
            prompt += projections

        # Append observation and instructions
        prompt += f"""

**Observation**:
- {data.summary}

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

            # The response from the current foken
            response += token

            # Yield the next part of the response
            yield response
