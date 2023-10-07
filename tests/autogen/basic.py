import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.append(_RePolyA)

from repolya._const import WORKSPACE_AUTOGEN, AUTOGEN_CONFIG
# from repolya._log import logger_autogen

from autogen import AssistantAgent, UserProxyAgent, config_list_from_json


config_list = config_list_from_json(env_or_file=str(AUTOGEN_CONFIG))

assistant = AssistantAgent(
    name="员工",
    llm_config={
        "config_list": config_list
    }
)

user_proxy = UserProxyAgent(
    name="me",
    code_execution_config={
        "work_dir": WORKSPACE_AUTOGEN
    }
)

user_proxy.initiate_chat(
    assistant,
    message="查找一下长沙的天气."
)

