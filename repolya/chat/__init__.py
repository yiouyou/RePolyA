import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'), override=True, verbose=True)

from ._openai import chat_predict_openai

