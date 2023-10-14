from repolya._const import AUTOGEN_CONFIG
from repolya._log import logger_autogen

from autogen import (
    AssistantAgent,
    UserProxyAgent,
    config_list_from_json,
)


config_list = config_list_from_json(env_or_file=str(AUTOGEN_CONFIG))

gpt4_config = {
    "config_list": config_list,
    "model": "gpt-4",
    "temperature": 0,
    "request_timeout": 120,
    "seed": 42,
}

##### planner
PLANNER_user = UserProxyAgent(
    name="PLANNER_user",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=0,  # terminate without auto-reply
)

PLANNER_planner = AssistantAgent(
    name="PLANNER_planner",
    llm_config=gpt4_config,
    system_message="You are a helpful AI assistant. You suggest coding and reasoning steps for another AI assistant to accomplish a task. Do not suggest concrete code. For any action beyond writing code or reasoning, convert it to a step which can be implemented by writing code. For example, the action of browsing the web can be implemented by writing code which reads and prints the content of a web page. Finally, inspect the execution result. If the plan is not good, suggest a better plan. If the execution is wrong, analyze the error and suggest a fix."
)

