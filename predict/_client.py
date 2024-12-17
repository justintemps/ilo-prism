from huggingface_hub import InferenceClient
import pandas as pd
import requests
from dotenv import load_dotenv
import os

load_dotenv()


class HuggingFaceClient:
    def __init__(self, model):
        self._token = os.getenv("HUGGING_FACE_TOKEN")
        self._client = InferenceClient(model, token=self._token)
