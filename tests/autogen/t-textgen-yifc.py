from autogen import (
    oai,
    AssistantAgent,
    UserProxyAgent,
    GroupChat,
    GroupChatManager,
)
import openai


# Configure OpenAI settings
openai.api_type = "openai"
openai.api_key = "..."
openai.api_base = "http://127.0.0.1:5552/v1"
openai.api_version = "2023-11-22"

#Use the local LLM server same as before
config_list = [
    {
        "model": "Yi-34B-200K-Llamafied-chat-SFT-function-calling-v3-GPTQ",
        "api_base": "http://127.0.0.1:5552/v1",
        "api_type": "open_ai",
        "api_key": "...",
    }
]

# set a "universal" config for the agents
agent_config = {
    "seed": 0,  # change the seed for different trials
    "temperature": 0.01,
    "config_list": config_list,
    "request_timeout": 300,
}

# humans
user_proxy = UserProxyAgent(
   name="Admin",
   system_message="A human admin. Interact with the planner to discuss the plan. Plan execution needs to be approved by this admin.",
   code_execution_config=False,
)

executor = UserProxyAgent(
    name="Executor",
    system_message="Executor. Execute the code written by the engineer and report the result.",
    human_input_mode="NEVER",
    code_execution_config={"last_n_messages": 3, "work_dir": "paper"},
)

# agents
engineer = AssistantAgent(
    name="Engineer",
    llm_config=agent_config,
    system_message='''Engineer. You follow an approved plan. You write python/shell code to solve tasks. Wrap the code in a code block that specifies the script type. The user can't modify your code. So do not suggest incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by the executor.
Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. Check the execution result returned by the executor.
If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
''',
)

scientist = AssistantAgent(
    name="Scientist",
    llm_config=agent_config,
    system_message="""Scientist. You follow an approved plan. You are able to categorize papers after seeing their abstracts printed. You don't write code."""
)

planner = AssistantAgent(
    name="Planner",
    system_message='''Planner. Suggest a plan. Revise the plan based on feedback from admin and critic, until admin approval.
The plan may involve an engineer who can write code and a scientist who doesn't write code.
Explain the plan first. Be clear which step is performed by an engineer, and which step is performed by a scientist.
''',
    llm_config=agent_config,
)

critic = AssistantAgent(
    name="Critic",
    system_message="Critic. Double check plan, claims, code from other agents and provide feedback. Check whether the plan includes adding verifiable info such as source URL.",
    llm_config=agent_config,
)

# start the "group chat" between agents and humans
groupchat = GroupChat(agents=[user_proxy, engineer, scientist, planner, executor, critic], messages=[], max_round=50)
manager = GroupChatManager(groupchat=groupchat, llm_config=agent_config)

# Start the Chat!
user_proxy.initiate_chat(
    manager,
    message="""
find papers on LLM applications from arxiv in the last week, create a markdown table of different domains.
""",
)

# to followup of the previous question, use:
# user_proxy.send(
#     recipient=assistant,
#     message="""your followup response here""",
# )
