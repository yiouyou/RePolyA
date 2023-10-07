from repolya._const import WORKSPACE_AUTOGEN, AUTOGEN_CONFIG
from repolya._log import logger_autogen

from autogen import (
    AssistantAgent,
    UserProxyAgent,
    config_list_from_json,
)
from autogen.agentchat.contrib.math_user_proxy_agent import MathUserProxyAgent


config_list = config_list_from_json(env_or_file=str(AUTOGEN_CONFIG))

##### Basic
A_user = UserProxyAgent(
    name="A_user",
    code_execution_config={
        "work_dir": WORKSPACE_AUTOGEN,
        "use_docker": False,
    },
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
)

A_assist = AssistantAgent(
    name="A_assist", 
    llm_config={
        "config_list": config_list,
        "request_timeout": 300,
        "seed": 42,
    },
    is_termination_msg=lambda x: True if "TERMINATE" in x.get("content") else False,
)

##### MATH
MATH_user = MathUserProxyAgent(
    name="MATH_user",
    code_execution_config={
        "use_docker": False
    },
    human_input_mode="NEVER",
)

MATH_assist = AssistantAgent(
    name="MATH_assist",     
    llm_config={
        "config_list": config_list,
        "request_timeout": 600,
        "seed": 42,
    },
    system_message="You are a helpful assistant.",
)


##### CODE
CODE_user = UserProxyAgent(
    name="CODE_user",
    code_execution_config={
        "work_dir": WORKSPACE_AUTOGEN,
        "last_n_messages": 2
    },
    human_input_mode="ALWAYS",
    system_message="A human admin who will give the idea and run the code provided by Coder.",
)

CODE_coder = AssistantAgent(
    name="CODE_coder",
    llm_config={
        "config_list": config_list,
        "request_timeout": 120,
        "seed": 42,
    },
)

CODE_pm = AssistantAgent(
    name="CODE_pm",
    llm_config={
        "config_list": config_list,
        "request_timeout": 120,
        "seed": 42,
    },
    system_message="You will help break down the initial idea into a well scoped requirement for the coder; Do not involve in future conversations or error fixing",
)


##### RD
RD_user = UserProxyAgent(
    name="RD_user",
    code_execution_config={
        "work_dir": WORKSPACE_AUTOGEN,
        "last_n_messages": 2
    },
    human_input_mode="TERMINATE",
    is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
)

RD_researcher = AssistantAgent(
    name="RD_researcher",
    llm_config={
        "config_list": config_list,
        "functions": [
            {
                "name": "search",
                "description": "google search for relevant information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Google search query",
                        }
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "scrape",
                "description": "scraping website content based on url",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "website url to scrape",
                        }
                    },
                    "required": ["url"],
                },
            }
        ],
    },
    system_message="Research about a given query, collect as many information as possible, and generate detailed research results with loads of technique details with all reference links attached; Add TERMINATE to the end of the research report;",
)


##### planner
PLANNER_user = UserProxyAgent(
    name="PLANNER_user",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=0,  # terminate without auto-reply
)

PLANNER_planner = AssistantAgent(
    name="PLANNER_planner",
    llm_config={
        "config_list": config_list,
        "request_timeout": 120,
        "seed": 42,
    },
    system_message="You are a helpful AI assistant. You suggest coding and reasoning steps for another AI assistant to accomplish a task. Do not suggest concrete code. For any action beyond writing code or reasoning, convert it to a step which can be implemented by writing code. For example, the action of browsing the web can be implemented by writing code which reads and prints the content of a web page. Finally, inspect the execution result. If the plan is not good, suggest a better plan. If the execution is wrong, analyze the error and suggest a fix."
)


##### PLAN_TASK
PLAN_TASK_user = UserProxyAgent(
    name="PLAN_user",
    code_execution_config={
        "work_dir": WORKSPACE_AUTOGEN,
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
        "functions": [
            {
                "name": "planner",
                "description": "ask planner to: 1. get a plan for finishing a task, 2. verify the execution result of the plan and potentially suggest new plan.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "question to ask planner. Make sure the question include enough context, such as the code and the execution result. The planner does not know the conversation between you and the user, unless you share the conversation with the planner.",
                        },
                    },
                    "required": ["message"],
                },
            },
        ],
    },
)


