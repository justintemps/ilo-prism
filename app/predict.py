from huggingface_hub import InferenceClient
from typing import Tuple

SYMSTEM_MESSAGE = "Summarize the data retrieved from the International Labour Organization's ILOSTAT database in a factual and objective tone. Limit the summary strictly to describing the data, focusing solely on patterns, figures, and relationships present in the tables, without adding context or analysis beyond the provided data."

MAX_TOKENS = 512

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
        return f"""This data comes from the dataset: {data_label}
                The geographic region for this data is: {area_label}
                The description of this dataset is: {data_description}
                Here is the data to analyse: {message}"""

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
