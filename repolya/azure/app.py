from repolya._log import logger_azure
from repolya.azure.model import DemoGPT

import os


openai_api_key = os.getenv("OPENAI_API_KEY")
openai_api_base = "https://api.openai.com/v1"
model_name = "gpt-3.5-turbo"

# demo_idea = "Create a system that can summarize a powerpoint file"
# demo_title = "PPT"


def run(demo_idea, demo_title):
    agent = DemoGPT(openai_api_key=openai_api_key, openai_api_base=openai_api_base)
    agent.setModel(model_name)
    for data in agent(demo_idea, demo_title):
        done = data.get("done", False)
        message = data.get("message", "")
        stage = data.get("stage", "stage")
        code = data.get("code", "")
        logger_azure.info(message)
        if done:
            print(code)
            break

