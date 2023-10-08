from repolya._const import WORKSPACE_AUTOGEN, AUTOGEN_CONFIG, AUTOGEN_DOC
from repolya._log import logger_autogen

from autogen import (
    AssistantAgent,
    UserProxyAgent,
    config_list_from_json,
)
from autogen.agentchat.contrib.math_user_proxy_agent import MathUserProxyAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
import chromadb

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
        "temperature": 0,
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
        "temperature": 0,
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
        "temperature": 0.1,
        "model": "gpt-4",
    },
)

CODE_pm = AssistantAgent(
    name="CODE_pm",
    llm_config={
        "config_list": config_list,
        "request_timeout": 120,
        "seed": 42,
        "temperature": 0,
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
        "temperature": 0,
        "model": "gpt-4",
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


##### RES
RES_user = UserProxyAgent(
   name="RES_user",
   system_message="A human admin. Interact with the planner to discuss the plan. Plan execution needs to be approved by this admin.",
   code_execution_config=False,
)

RES_engineer = AssistantAgent(
    name="RES_engineer",
    llm_config={
        "config_list": config_list,
        "request_timeout": 120,
        "seed": 42,
        "temperature": 0,
        "model": "gpt-4",
    },
    system_message='''Engineer. You follow an approved plan. You write python/shell code to solve tasks. Wrap the code in a code block that specifies the script type. The user can't modify your code. So do not suggest incomplete code which requires others to modify. Don't use a code block if it's not intended to be executed by the executor.
Don't include multiple code blocks in one response. Do not ask others to copy and paste the result. Check the execution result returned by the executor.
If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try.
''',
)

RES_scientist = AssistantAgent(
    name="RES_scientist",
    llm_config={
        "config_list": config_list,
        "request_timeout": 120,
        "seed": 42,
        "temperature": 0,
        "model": "gpt-4",
    },
    system_message="Scientist. You follow an approved plan. You are able to categorize papers after seeing their abstracts printed. You don't write code."
)

RES_planner = AssistantAgent(
    name="RES_planner",
    system_message='''Planner. Suggest a plan. Revise the plan based on feedback from admin and critic, until admin approval.
The plan may involve an engineer who can write code and a scientist who doesn't write code.
Explain the plan first. Be clear which step is performed by an engineer, and which step is performed by a scientist.
''',
    llm_config={
        "config_list": config_list,
        "request_timeout": 120,
        "seed": 42,
        "temperature": 0,
        "model": "gpt-4",
    },
)

RES_executor = UserProxyAgent(
    name="RES_executor",
    code_execution_config={
        "work_dir": WORKSPACE_AUTOGEN,
        "last_n_messages": 3,
    },
    system_message="Executor. Execute the code written by the engineer and report the result.",
    human_input_mode="NEVER",
)

RES_critic = AssistantAgent(
    name="RES_critic",
    llm_config={
        "config_list": config_list,
        "request_timeout": 120,
        "seed": 42,
        "temperature": 0,
        "model": "gpt-4",
    },
    system_message="Critic. Double check plan, claims, code from other agents and provide feedback. Check whether the plan includes adding verifiable info such as source URL.",
)


##### RAG
def RAG_DOC_user(docs_path, model, collection_name):
    _RAG_DOC_user = RetrieveUserProxyAgent(
        name="RAG_DOC_user",
        retrieve_config={
            "task": "qa",
            "docs_path": docs_path,
            "chunk_token_size": 2000,
            "model": model,
            "client": chromadb.PersistentClient(path="/tmp/chromadb"),
            "collection_name": collection_name,
            "embedding_model": "all-MiniLM-L12-v2",
            "chunk_mode": "one_line", # multi_lines
        },
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
    )
    return _RAG_DOC_user

def RAG_CODE_user(docs_path, model, collection_name):
    _RAG_CODE_user = RetrieveUserProxyAgent(
        name="RAG_CODE_user",
        retrieve_config={
            "task": "code",
            "docs_path": docs_path,
            "chunk_token_size": 2000,
            "model": model,
            "client": chromadb.PersistentClient(path="/tmp/chromadb"),
            "collection_name": collection_name,
            "embedding_model": "all-mpnet-base-v2",
            "chunk_mode": "multi_lines", # one_line
        },
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
    )
    return _RAG_CODE_user

RAG_assist = RetrieveAssistantAgent(
    name="RAG_CODE_assist",
    llm_config={
        "config_list": config_list,
        "request_timeout": 600,
        "seed": 42,
    },
    system_message="You are a helpful assistant.",
)

