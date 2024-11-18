from huggingface_hub import InferenceClient

SYMSTEM_MESSAGE = "Summarize the data retrieved from the International Labour Organization's ILOSTAT database in a factual and objective tone. Limit the summary strictly to describing the data, focusing solely on patterns, figures, and relationships present in the tables, without adding context or analysis beyond the provided data."

MAX_TOKENS = 512

TEMPERATURE = 0.7


class AppPredictor:

    def __init__(self, model: str, token):
        self.__client = InferenceClient(model, token=token)

    # This is a Generator callback that is used by the Interface client to yield responses
    def respond(
        self,
        message,
        system_message=SYMSTEM_MESSAGE,
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
    ):
        # Initialize the messages with the first system message
        messages = [{"role": "system", "content": system_message}]

        # Adds the current message from the user
        messages.append({"role": "user", "content": message})

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
