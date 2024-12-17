import os
from ilostat.ilostat import ILOStat

# Chatbot Model
CHATBOT_MODEL = "HuggingFaceH4/zephyr-7b-beta"

# Summarization Model
SUMMARIZATION_MODEL = "facebook/bart-large-cnn"

# Default area
default_area = "X01"

# Default dataflow
default_dataflow = "DF_UNE_2EAP_SEX_AGE_RT"

# Setup ILOStat Client
ilostat = ILOStat("en")
