from huggingface_hub import InferenceClient
import pandas as pd
import requests
from dotenv import load_dotenv
import os

load_dotenv()


SYMSTEM_MESSAGE = "Generate a concise summary of the labour statistics data retrieved from the International Labour Organization's ILOSTAT database, using a factual and objective tone. Focus strictly on patterns, trends, figures, and relationships evident in the data table, without providing contextual explanations or interpretations beyond the data itself. Highlight notable changes in values, any observable trends over time, and relevant statistical shifts as presented in the data."

MAX_TOKENS = 1000

TEMPERATURE = 0.7

token = os.getenv("HUGGING_FACE_TOKEN")

API_URL = "https://api-inference.huggingface.co/models/google/tapas-large-finetuned-wtq"
headers = {"Authorization": f"Bearer {token}"}


class AppPredictor:

    def __init__(self, model: str, token):
        self.__client = InferenceClient(model, token=token)

    # Serialize the table into Tapex-compatible format

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

    # This is a Generator callback that is used by the Interface client to yield responses
    def chat_completion(
        self,
        df: pd.DataFrame,
        area_label: str,
        data_label: str,
        data_description=str,
        system_message=SYMSTEM_MESSAGE,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
    ):
        # Initialize the messages with the first system message
        messages = [{"role": "system", "content": system_message}]

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
        for msg in self.__client.chat_completion(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        ):
            # The current token
            token = msg.choices[0].delta.content

            # The response from the current foken
            response += token

            # Yield the next part of the response
            yield response

    # Use post method to send the model a formatted query
    # https://huggingface.co/docs/huggingface_hub/v0.26.5/en/guides/inference#legacy-inferenceapi-client
    def table_question_answering(
        self,
        df: pd.DataFrame,
        area_label: str,
        data_label: str,
        data_description=str,
        system_message=SYMSTEM_MESSAGE,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
    ):

        new_df = df[["TIME_PERIOD", "value"]].copy()

        new_col_names = {"TIME_PERIOD": "year", "value": "Global Unemployment Rate"}

        new_df.rename(columns=new_col_names, inplace=True)

        df_str = new_df.astype(str)
        table = df_str.to_dict(orient="list")
        print(table)

        def query(payload):
            response = requests.post(API_URL, headers=headers, json=payload)
            return response.json()

        output = query(
            {
                "inputs": {
                    "query": "Is global unemployment trending up or down?",
                    "table": table,
                }
            }
        )

        return output


if __name__ == "__main__":
    pass
