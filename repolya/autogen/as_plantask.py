from repolya._const import AUTOGEN_CONFIG
from repolya._log import logger_autogen

from repolya.autogen.tool_function import (
    planner,
    _def_planner,
)

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
        **base_config,
        "functions": [_def_planner],
    },
    function_map={
        "planner": planner,
    },
)

