import os
from ilostat.ilostat import ILOStat
from .predict import AppPredictor
from dotenv import load_dotenv

load_dotenv()

# Model to use
MODEL = "microsoft/tapex-base"
# MODEL = "HuggingFaceH4/zephyr-7b-beta"

# Hugging face token
HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN")

# LLM Client object
default_client = AppPredictor(MODEL, token=HUGGING_FACE_TOKEN)

# Default area
default_area = "X01"

# Default dataflow
default_dataflow = "DF_UNE_2EAP_SEX_AGE_RT"

# Setup ILOStat Client
ilostat = ILOStat("en")
