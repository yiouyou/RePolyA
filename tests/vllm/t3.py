import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.append(_RePolyA)

# from langchain.llms import VLLMOpenAI
from repolya.local.vllm import VLLMOpenAI


# python -m vllm.entrypoints.openai.api_server --model models/TheBloke_SUS-Chat-34B-AWQ


llm = VLLMOpenAI(
    openai_api_key="EMPTY",
    openai_api_base="http://localhost:8000/v1",
    model_name="models/TheBloke_SUS-Chat-34B-AWQ",
    model_kwargs={"stop": ["."]},
)
print(llm("Rome is"))

