from repolya._const import AUTOGEN_CONFIG
from repolya._log import logger_autogen

from autogen import (
    AssistantAgent,
    UserProxyAgent,
    config_list_from_json,
)
from autogen.agentchat.contrib.math_user_proxy_agent import MathUserProxyAgent


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


##### MATH
MATH_user = MathUserProxyAgent(
    name="MATH_user",
    code_execution_config={
        "work_dir": 'math',
        "use_docker": False
    },
    human_input_mode="NEVER",
)

MATH_assist = AssistantAgent(
    name="MATH_assist",     
    llm_config=base_config,
    system_message="You are a helpful assistant.",
)

