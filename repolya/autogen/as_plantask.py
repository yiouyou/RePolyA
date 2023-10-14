from repolya._const import AUTOGEN_CONFIG
from repolya._log import logger_autogen

from repolya.autogen.tool import plantask_functions

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

##### plan task
PLAN_TASK_user = UserProxyAgent(
    name="PLAN_user",
    code_execution_config={
        "work_dir": 'planned_task',
    },
    human_input_mode="TERMINATE",
    max_consecutive_auto_reply=10,
)

PLAN_TASK_assist = AssistantAgent(
    name="PLAN_assist",
    llm_config={
        "config_list": config_list,
        "request_timeout": 600,
        "seed": 42,
        "temperature": 0,
        "model": "gpt-4",
        "functions": plantask_functions,
    },
)

