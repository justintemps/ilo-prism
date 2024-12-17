import pandas as pd
from ._client import HuggingFaceClient


class ChatBot(HuggingFaceClient):
    def __init__(self, model):
        super().__init__(model)

        self.SYSTEM_MESSAGE = "Generate a concise summary of the labour statistics data retrieved from the International Labour Organization's ILOSTAT database, using a factual and objective tone. Focus strictly on patterns, trends, figures, and relationships evident in the data table, without providing contextual explanations or interpretations beyond the data itself. Highlight notable changes in values, any observable trends over time, and relevant statistical shifts as presented in the data."

        self.MAX_TOKENS = 1000

        self.TEMPERATURE = 0.7

    def _serialize_dataframe(self, df: pd.DataFrame):

        # Get column headers
        headers = " | ".join(df.columns)

        # Get rows as strings
        rows = [" | ".join(map(str, row)) for row in df.values]

        # Combine headers and rows
        serialized_table = f"| {headers} |\n" + "\n".join(
            [f"| {row} |" for row in rows]
        )
        return serialized_table

    def _format_message(
        self,
        df: pd.DataFrame,
        area_label: str,
        data_label: str,
        data_description: str,
    ):

        table = self._serialize_dataframe(df)

        return f"""The dataset represents: {data_label}
                Geographic scope: {area_label}
                Dataset description: {data_description}
                Table data overview: {table}"""

    def respond(
        self,
        df: pd.DataFrame,
        area_label: str,
        data_label: str,
        data_description=str,
    ):
        # Initialize the messages with the first system message
        messages = [{"role": "system", "content": self.SYSTEM_MESSAGE}]

        user_message = self._format_message(
            df=df,
            area_label=area_label,
            data_label=data_label,
            data_description=data_description,
        )

        # Adds the current message from the user
        messages.append({"role": "user", "content": user_message})

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
