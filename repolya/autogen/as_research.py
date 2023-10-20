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
    "request_timeout": 120,
    "temperature": 0,
    "model": "gpt-4",
    # "use_cache": False,
    "seed": 42,
}


##### RES
USER_PROMPT = "A human admin. You interact with the planner to discuss the plan. Plan execution needs to be approved by this admin."
RES_user = UserProxyAgent(
   name="RES_user",
   code_execution_config=False,
   system_message=USER_PROMPT,
)


EXECUTOR_PROMPT = "Executor. Execute the code written by the engineer and report the result."
RES_executor = UserProxyAgent(
    name="RES_executor",
    code_execution_config={
        "work_dir": 'research',
        "last_n_messages": 3,
        "use_docker": False,
    },
    human_input_mode="NEVER",
    system_message=EXECUTOR_PROMPT,
)


ENGINEER_PROMPT = "Engineer. You follow an approved plan. You write python/shell code to solve tasks. Wrap the code in a code block that specifies the script type. The user can't modify your code. So do not suggest incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by the executor. Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. Check the execution result returned by the executor. If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try."
RES_engineer = AssistantAgent(
    name="RES_engineer",
    llm_config=base_config,
    system_message=ENGINEER_PROMPT,
)


SCIENTIST_PROMPT = "Scientist. You follow an approved plan. You are able to categorize papers after seeing their abstracts printed. You don't write code."
RES_scientist = AssistantAgent(
    name="RES_scientist",
    llm_config=base_config,
    system_message=SCIENTIST_PROMPT,
)


PLANNER_PROMPT = "Planner. Suggest a plan. Revise the plan based on feedback from admin and critic, until admin approval. The plan may involve an engineer who can write code and a scientist who doesn't write code. Explain the plan first. Be clear which step is performed by an engineer, and which step is performed by a scientist."
RES_planner = AssistantAgent(
    name="RES_planner",
    llm_config=base_config,
    system_message=PLANNER_PROMPT,
)


CRITIC_PROMPT = "Critic. Double check plan, claims, code from other agents and provide feedback. Check whether the plan includes adding verifiable info such as source URL."
RES_critic = AssistantAgent(
    name="RES_critic",
    llm_config=base_config,
    system_message=CRITIC_PROMPT,
)

