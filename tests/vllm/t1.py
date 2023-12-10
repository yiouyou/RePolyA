import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.append(_RePolyA)

from repolya.local.vllm import VLLM, get_vllm_llm


_model = "/home/songz/text-generation-webui/models/TheBloke_SUS-Chat-34B-AWQ"

# llm1 = VLLM(
#     model=_model,
#     trust_remote_code=True,
#     temperature=0.01,
#     top_p=0.9,
#     max_new_tokens=200,
#     stop=[""],
# )
# print(llm1("### Human:\nWhat is the capital of France?\n\n### Assistant:\n"))

llm2 = get_vllm_llm(_model,
                    0.01,
                    0.9,
                    200,
                    [""]
)
print(llm2("### Human:\n太阳系的行星有哪些？\n\n### Assistant:\n"))

