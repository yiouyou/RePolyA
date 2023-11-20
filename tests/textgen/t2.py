from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from textgen import TextGen
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.globals import set_debug

set_debug(True)


model_url = "http://127.0.0.1:5552"

template = """Question: {question}

Answer: Let's think step by step."""
prompt = PromptTemplate(template=template, input_variables=["question"])

question = "What NFL team won the Super Bowl in the year Justin Bieber was born?"

llm = TextGen(
    model_url=model_url,
    temperature=0.01,
    top_p=0.9,
    seed=10,
    max_tokens=200,
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()]
)

llm_chain = LLMChain(prompt=prompt, llm=llm)
llm_chain.run(question)

# curl http://127.0.0.1:5552/v1/completions -H "Content-Type: application/json" -d '{"prompt": "Question: What NFL team won the Super Bowl in the year Justin Bieber was born?\n\nAnswer: Let us think step by step.", "max_tokens": 200, "temperature": 0.01 ,"top_p": 0.9, "seed": 10, "stream": true}'

