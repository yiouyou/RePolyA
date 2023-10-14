import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.append(_RePolyA)

from repolya.autogen.workflow import do_math
from repolya.autogen.util import cost_usage
from autogen import ChatCompletion


ChatCompletion.start_logging(reset_counter=True, compact=False)


_task='''Find all numbers $a$ for which the graph of $y=x^2+a$ and the graph of $y=ax$ intersect. Express your answer in interval notation.'''
re = do_math(_task)
print(f"out: '{re}'")
print(f"cost_usage: {cost_usage(ChatCompletion.logged_history)}")


# import os
# from dotenv import load_dotenv
# load_dotenv(os.path.join(_RePolyA, '.env'), override=True, verbose=True)

# from repolya._const import WORKSPACE_AUTOGEN, AUTOGEN_CONFIG
# from repolya._log import logger_autogen

# from autogen import AssistantAgent, UserProxyAgent, config_list_from_json
# from autogen.agentchat.contrib.math_user_proxy_agent import MathUserProxyAgent
# import autogen


# config_list = config_list_from_json(env_or_file=str(AUTOGEN_CONFIG))

# # autogen.ChatCompletion.start_logging()

# assistant = autogen.AssistantAgent(
#     name="assistant", 
#     system_message="You are a helpful assistant.",
#     llm_config={
#         "request_timeout": 600,
#         "seed": 42,
#         "config_list": config_list,
#     }
# )

# mathproxyagent = MathUserProxyAgent(
#     name="mathproxyagent", 
#     human_input_mode="NEVER",
#     code_execution_config={"use_docker": False},
# )

# math_problem = "Find all $x$ that satisfy the inequality $(2x+10)(x+3)<(3x+9)(x+8)$. Express your answer in interval notation."
# mathproxyagent.initiate_chat(assistant, problem=math_problem)

# math_problem = "Find all numbers $a$ for which the graph of $y=x^2+a$ and the graph of $y=ax$ intersect. Express your answer in interval notation."
# mathproxyagent.initiate_chat(assistant, problem=math_problem, prompt_type="two_tools")
