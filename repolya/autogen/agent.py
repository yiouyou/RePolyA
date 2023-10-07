from repolya._const import WORKSPACE_AUTOGEN, AUTOGEN_CONFIG
from repolya._log import logger_autogen

from autogen import (
    AssistantAgent,
    UserProxyAgent,
    config_list_from_json
)
from autogen.agentchat.contrib.math_user_proxy_agent import MathUserProxyAgent


config_list = config_list_from_json(env_or_file=str(AUTOGEN_CONFIG))

##### A_user
A_user = UserProxyAgent(
    name="A_user",
    code_execution_config={
        "work_dir": WORKSPACE_AUTOGEN,
    }
)

##### A_assist
A_assist = AssistantAgent(
    name="A_assist", 
    llm_config={
        "request_timeout": 300,
        "seed": 42,
        "config_list": config_list,
    },
    # system_message="You are a helpful assistant.",
)

##### A_math
A_math = MathUserProxyAgent(
    name="A_math", 
    human_input_mode="NEVER",
    code_execution_config={
        "use_docker": False
    },
)


##### CODE
CODE_user = UserProxyAgent(
    name="CODE_user",
    code_execution_config={
        "work_dir": WORKSPACE_AUTOGEN,
        "last_n_messages": 2
    },
    system_message="A human admin who will give the idea and run the code provided by Coder.",
    human_input_mode="ALWAYS",
)

CODE_coder = AssistantAgent(
    name="CODE_coder",
    llm_config={
        "request_timeout": 120,
        "seed": 42,
        "config_list": config_list,
    },
)

CODE_pm = AssistantAgent(
    name="CODE_pm",
    llm_config={
        "request_timeout": 120,
        "seed": 42,
        "config_list": config_list,
    },
    system_message="You will help break down the initial idea into a well scoped requirement for the coder; Do not involve in future conversations or error fixing",
)


##### RD
RD_user = UserProxyAgent(
    name="RD_user",
    code_execution_config={
        "work_dir": WORKSPACE_AUTOGEN,
        "last_n_messages": 2
    },
    is_termination_msg=lambda x: x.get("content", "") and x.g("content", "").rstrip().endswith("TERMINATE"),
    human_input_mode="TERMINATE",
)

llm_config_researcher = {
    "functions": [
        {
            "name": "search",
            "description": "google search for relevant information",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Google search query",
                    }
                },
                "required": ["query"],
            },
        },
        {
            "name": "scrape",
            "description": "scraping website content based on url",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "website url to scrape",
                    }
                },
                "required": ["url"],
            },
        }
    ],
    "config_list": config_list
}

RD_researcher = AssistantAgent(
    name="RD_researcher",
    system_message="Research about a given query, collect as many information as possible, and generate detailed research results with loads of technique details with all reference links attached; Add TERMINATE to the end of the research report;",
    llm_config=llm_config_researcher,
)


