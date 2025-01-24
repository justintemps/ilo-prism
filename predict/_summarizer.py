from ._client import HuggingFaceClient
from ilostat.ilostat import ILOStat


class MetadataSummarizer(HuggingFaceClient):
    def __init__(self, dataflow: str, model="facebook/bart-large-cnn"):
        super().__init__(model)

        self.dataflow = dataflow

        self.metadata = ILOStat("en").get_dataflow_description(self.dataflow)

    def respond(self) -> str:

        result = self._client.summarization(self.metadata)

        return result.summary_text


if __name__ == "__main__":
    from app.defaults import AppDefaults

    dataflow = AppDefaults().dataflow

    summarizer = MetadataSummarizer(dataflow)

    print(summarizer.respond())
