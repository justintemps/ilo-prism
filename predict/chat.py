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

            standardized_change = (
                abs(previous_value - current_value) / data.standard_deviation
            )

            magnitude = ""

            if standardized_change > 3:
                magnitude = "Dramatic"
            elif 2 < standardized_change <= 3:
                magnitude = "Substantial"
            elif 1 < standardized_change <= 2:
                magnitude = "Moderate"
            elif 0.5 < standardized_change <= 1:
                magnitude = "Modest"
            else:
                magnitude = "Slight"

            if current_value > previous_value:
                summary_lines.append(f"{magnitude} increase: {year} = {current_value}")
            elif current_value < previous_value:
                summary_lines.append(f"{magnitude} decrease: {year} = {current_value}")

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

    def print_dimensions(self, data: DataDescriptor) -> str:
        # Get the dimensions of the data
        dimensions = data.dimensions

        # Initialize the result string
        result = ""

        # Add each dimension to the result
        for dimension, value in dimensions:
            result += f"- {dimension}: {value}\n"

        return result

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

**Dimensions**
{self.print_dimensions(data)}
**Key Metrics**
{self.print_metrics(data)}
{self.print_projections(data)}

**Observation**
- {data.trend}

**Instructions**
1. Summarize the general trend of the data in a single paragraph of four or five sentences.
2. Focus on overall patterns, key increases or decreases, peaks, and minimums.
3. Use clear and concise language suitable for a general audience.

Your response should be coherent, factual, and easy to understand.
"""

        return prompt

    def respond(self, prompt: str, yield_tokens: bool = False):
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

            if not yield_tokens:
                yield response
            else:
                yield token


if __name__ == "__main__":
    from app.defaults import AppDefaults
    from textwrap import fill, wrap

    # Set a default model for the chatbot
    model = "meta-llama/Llama-3.3-70B-Instruct"

    # Instantiate the chatbot
    chatbot = ChatBot(model)

    # Get the initial settings
    initial = AppDefaults()

    # Get the area, dataflow, and dataframe
    area_label = initial.area_label
    dataflow_label = initial.dataflow_label
    dataframe = initial.dataframe

    # Create a data descriptor
    descriptor = DataDescriptor(dataframe)

    # Print the prompt
    prompt = chatbot.prompt(dataframe, area_label, dataflow_label)

    # Gather the response
    response_paragraph = []

    # Generate a response
    for response in chatbot.respond(prompt, yield_tokens=True):
        # Append only the new, non-repeated portion
        response_paragraph.append(response)

    # Join fragments into a single paragraph
    response_paragraph = "".join(response_paragraph).strip()

    # Wrap the paragraph to a specific width
    response_paragraph = fill(response_paragraph, width=80)

    # Now let's format the prompt
    wrapped_prompt = []
    for line in prompt.splitlines():
        # Wrap only if the line is not empty
        if line.strip():
            wrapped_prompt.extend(wrap(line, width=80))
        else:
            wrapped_prompt.append("")
    wrapped_prompt = "\n".join(wrapped_prompt)

    # Print the formatted prompt and response
    print("\n")
    print("-" * 36, "PROMPT", "-" * 36)
    print(wrapped_prompt, "\n")
    print("-" * 36, "RESPONSE", "-" * 36)
    print(response_paragraph, "\n")
