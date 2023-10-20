from repolya._const import AUTOGEN_CONFIG
from repolya._log import logger_autogen

from autogen import (
    AssistantAgent,
    UserProxyAgent,
    config_list_from_json,
)


config_list = config_list_from_json(env_or_file=str(AUTOGEN_CONFIG))


# Base Configuration
base_config = {
    "config_list": config_list,
    "request_timeout": 300,
    "temperature": 0,
    "model": "gpt-4",
    # "use_cache": False,
    "seed": 42,
}


##### Basic
A_user = UserProxyAgent(
    name="A_user",
    code_execution_config={
        "work_dir": 'basic',
        "use_docker": False,
    },
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
)


A_assist = AssistantAgent(
    name="A_assist", 
    llm_config=base_config,
    is_termination_msg=lambda x: True if "TERMINATE" in x.get("content") else False,
)

