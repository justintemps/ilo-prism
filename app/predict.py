from huggingface_hub import InferenceClient
from typing import Tuple

SYMSTEM_MESSAGE = "Generate a concise summary of the labour statistics data retrieved from the International Labour Organization's ILOSTAT database, using a factual and objective tone. Focus strictly on patterns, trends, figures, and relationships evident in the data table, without providing contextual explanations or interpretations beyond the data itself. Highlight notable changes in values, any observable trends over time, and relevant statistical shifts as presented in the data."

MAX_TOKENS = 1000

TEMPERATURE = 0.7


class AppPredictor:

    def __init__(self, model: str, token):
        self.__client = InferenceClient(model, token=token)

    def _embellish_message(
        self,
        message: str,
        area_label: str,
        data_label: str,
        data_description: str,
    ):
        return f"""The dataset represents: {data_label}
                Geographic scope:: {area_label}
                Dataset description: {data_description}
                Table data overview: {message}"""

    # This is a Generator callback that is used by the Interface client to yield responses
    def respond(
        self,
        message: str,
        area_label: str,
        data_label: str,
        data_description=str,
        system_message=SYMSTEM_MESSAGE,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
    ):
        # Initialize the messages with the first system message
        messages = [{"role": "system", "content": system_message}]

        user_message = self._embellish_message(
            message,
            area_label=area_label,
            data_label=data_label,
            data_description=data_description,
        )

        # Adds the current message from the user
        messages.append({"role": "user", "content": user_message})

        print(messages)

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
