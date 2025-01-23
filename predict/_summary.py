from ._client import HuggingFaceClient


class DatastreamSummaryBot(HuggingFaceClient):
    def __init__(self, model, description: str):
        super().__init__(model)

        self.description = description

        self.MAX_TOKENS = 1000

        self.TEMPERATURE = 0.2

    def respond(self) -> str:
        messages = [
            {
                "role": "system",
                "content": "You are a specialized chatbot designed to summarize lengthy texts about statistical datastreams into concise and plain English. Your summaries should provide clear context and key insights that can be easily understood by someone unfamiliar with technical jargon. Your output will be used by another chatbot that summarizes statistical data for end users, so your summaries must focus on: \n\n1. The main purpose or objective of the datastream.\n2. The type of data it includes and its source.\n3. Any notable trends, patterns, or key points mentioned.\n4. How the datastream is used or its practical applications.\n\nAvoid including unnecessary technical details or lengthy explanations. Ensure your summaries are accurate, coherent, and formatted clearly for ease of understanding.",
            }
        ]

        messages.append({"role": "user", "content": self.description})

        result = self._client.chat_completion(
            messages=messages,
            max_tokens=self.MAX_TOKENS,
            temperature=self.TEMPERATURE,
            stream=False,
        )

        return result.choices[0].message.content


if __name__ == "__main__":
    from ilostat.ilostat import ILOStat
    from app.defaults import AppDefaults

    initial = AppDefaults()

    dataflow = initial.dataflow
    dataflow_label = initial.dataflow_label
    dataflow_summary = ILOStat("en").get_dataflow_description(dataflow)

    ilostat = ILOStat("en")

    model = "meta-llama/Llama-3.3-70B-Instruct"

    summaryBot = DatastreamSummaryBot(model, dataflow_summary)

    print(summaryBot.respond())
