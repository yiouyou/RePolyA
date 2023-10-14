import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.append(_RePolyA)

from repolya.autogen.workflow import do_simple_task, do_plan_task
from repolya.autogen.util import cost_usage
from autogen import ChatCompletion


ChatCompletion.start_logging(reset_counter=True, compact=False)


_n = int(sys.argv[1])

if _n == 1:
    _task='''查找一下长沙的天气.'''
    re = do_simple_task(_task)
    print(f"out: '{re}'")


if _n == 2:
    _task='''Suggest a fix to an open good first issue of flaml.'''
    re = do_plan_task(_task)
    print(f"out: '{re}'")


print(f"cost_usage: {cost_usage(ChatCompletion.logged_history)}")


# import os
# from dotenv import load_dotenv
# load_dotenv(os.path.join(_RePolyA, '.env'), override=True, verbose=True)

# from repolya._const import WORKSPACE_AUTOGEN, AUTOGEN_CONFIG
# from repolya._log import logger_autogen

# from autogen import (
#     AssistantAgent,
#     UserProxyAgent,
#     config_list_from_json,
#     ChatCompletion,
# )
# ChatCompletion.start_logging()


# config_list = config_list_from_json(env_or_file=str(AUTOGEN_CONFIG))

# assistant = AssistantAgent(
#     name="员工",
#     llm_config={
#         "config_list": config_list
#     }
# )

# user_proxy = UserProxyAgent(
#     name="me",
#     code_execution_config={
#         "work_dir": WORKSPACE_AUTOGEN
#     }
# )

# user_proxy.initiate_chat(
#     assistant,
#     message="查找一下长沙的天气."
# )


# import json
# with open(WORKSPACE_AUTOGEN /'_talk_autogen.json', 'w') as wf:
#     wf.write(json.dumps(ChatCompletion.logged_history, indent=4, ensure_ascii=False))

