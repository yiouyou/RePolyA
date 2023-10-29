from repolya._const import AUTOGEN_CONFIG
from repolya._log import logger_autogen

from autogen import (
    AssistantAgent,
    UserProxyAgent,
    config_list_from_json,
)
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
import chromadb

from repolya.autogen.tool_function import (
    qa_faiss_openai_frank,
    _def_qa_faiss_openai_frank,
    qa_summerize,
    _def_qa_summerize,
)


config_list = config_list_from_json(env_or_file=str(AUTOGEN_CONFIG))
is_termination_msg = lambda x: isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()
# lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE")
# lambda x: True if "TERMINATE" in x.get("content") else False


# Base Configuration
base_config = {
    "config_list": config_list,
    "request_timeout": 300,
    "temperature": 0,
    "model": "gpt-3.5-turbo",
    "use_cache": False,
    # "seed": 42,
}


##### RAG
def RAG_DOC_user(docs_path, model, collection_name):
    _RAG_DOC_user = RetrieveUserProxyAgent(
        name="RAG_DOC_user",
        retrieve_config={
            "task": "qa",
            "docs_path": docs_path,
            "model": model,
            "client": chromadb.PersistentClient(path="/tmp/chromadb"),
            "collection_name": collection_name,
            "embedding_model": "all-mpnet-base-v2", #"all-MiniLM-L12-v2",
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
    name="RAG_assist",
    llm_config=base_config,
    system_message="You are a helpful assistant.",
)


#### boss, etc.
BOSS_PROMPT = "The boss who ask questions and give tasks."
RAG_boss = UserProxyAgent(
    name="RAG_boss",
    code_execution_config=False,
    human_input_mode="TERMINATE",
    is_termination_msg=is_termination_msg,
    system_message=BOSS_PROMPT,
)


BOSS_AID_PROMPT = "Assistant who has extra content retrieval power for solving difficult problems."
def RAG_boss_aid(docs_path, model, collection_name):
    _RAG_boss_aid = RetrieveUserProxyAgent(
        name="RAG_boss_aid",
        retrieve_config={
            "task": "code",
            "docs_path": docs_path,
            "chunk_token_size": 1000,
            "model": model,
            "client": chromadb.PersistentClient(path="/tmp/chromadb"),
            "collection_name": collection_name,
            "get_or_create": True,
        },
        code_execution_config=False,
        human_input_mode="TERMINATE",
        is_termination_msg=is_termination_msg,
        max_consecutive_auto_reply=3,
        system_message=BOSS_AID_PROMPT,
    )
    return _RAG_boss_aid


PM_PROMPT = "You are a product manager. Reply `TERMINATE` in the end when everything is done."
RAG_pm = AssistantAgent(
    name="RAG_pm",
    llm_config=base_config,
    is_termination_msg=is_termination_msg,
    system_message=PM_PROMPT,
)


ENGINEER_PROMPT = "You are a senior python engineer. Reply `TERMINATE` in the end when everything is done."
RAG_engineer = AssistantAgent(
    name="RAG_engineer",
    llm_config=base_config,
    is_termination_msg=is_termination_msg,
    system_message=ENGINEER_PROMPT,
)


REVIEWER_PROMPT = "You are a code reviewer. Reply `TERMINATE` in the end when everything is done."
RAG_reviewer = AssistantAgent(
    name="RAG_reviewer",
    is_termination_msg=is_termination_msg,
    system_message=REVIEWER_PROMPT,
)


##### Organizer
COMPLETION_PROMPT = "If everything looks good, respond with APPROVED."

USER_PROMPT = "User. You ask the Planner questions and assign tasks."
RAG_task_user = UserProxyAgent(
    name="RAG_user",
    code_execution_config=False,
    human_input_mode="NEVER",
    is_termination_msg=is_termination_msg,
    system_message=USER_PROMPT,
)


PLANNER_PROMPT = "Planner. To help the User to collect information and evidence out of a personal information database, you need to break down complex questions into simpler sub-questions (no more than THREE) for easier answer retrieval from the database. Send the list to the the Critic for review. And adjust the list based on the Critic's feedback, keep the number of questions around FIVE. Output the list only, no comments, nothing else."
RAG_task_planner = AssistantAgent(
    name="RAG_task_planner",
    llm_config=base_config,
    code_execution_config=False,
    is_termination_msg=is_termination_msg,
    system_message=PLANNER_PROMPT,
)


CRITIC_PROMPT = "Critic. Double check the list of sub-questions from Planner and provide feedback."
RAG_task_critic = AssistantAgent(
    name="RAG_task_critic",
    llm_config=base_config,
    is_termination_msg=is_termination_msg,
    system_message=CRITIC_PROMPT,
)


##### Organizer
USER_PROMPT_ZH = "作为'用户'，你向'规划师'提出问题并分配任务。"
RAG_task_user_zh = UserProxyAgent(
    name="RAG_task_用户",
    code_execution_config=False,
    human_input_mode="NEVER",
    is_termination_msg=is_termination_msg,
    system_message=USER_PROMPT_ZH,
)


PLANNER_PROMPT_ZH = "作为'规划师'，你为了帮助'用户'收集相关信息，需要将复杂的问题分解为更简单的子问题（不超过3个），以便更轻松地从互联网或者数据库中搜集信息。你将子问题列表发送给'评判者'进行审查。并根据'评判者'的反馈调整列表，保持问题数量在5个左右。只输出子问题列表，不用注释，没其他任何内容。"
RAG_task_planner_zh = AssistantAgent(
    name="RAG_task_规划师",
    llm_config=base_config,
    code_execution_config=False,
    is_termination_msg=is_termination_msg,
    system_message=PLANNER_PROMPT_ZH,
)


CRITIC_PROMPT_ZH = "作为'评判者'，你仔细检查'规划师'提供的子问题列表并提供反馈。"
RAG_task_critic_zh = AssistantAgent(
    name="RAG_task_评判者",
    llm_config=base_config,
    is_termination_msg=is_termination_msg,
    system_message=CRITIC_PROMPT_ZH,
)


# SEARCHER_PROMPT = "Searcher. You use given function to search for information in the database."
# RAG_task_searcher = AssistantAgent(
#     name="RAG_task_searcher",
#     llm_config={
#         **base_config,
#         "functions": [_def_qa_faiss_openai_frank],
#     },
#     function_map={
#         "qa_faiss_openai_frank": qa_faiss_openai_frank,
#     },
#     code_execution_config=False,
#     is_termination_msg=is_termination_msg,
#     system_message=SEARCHER_PROMPT,
# )


# SUMMERIZER_PROMPT = "Summerizer. You use given function to summerize a given text. Reply `TERMINATE` in the end when everything is done."
# RAG_task_summerizer = AssistantAgent(
#     name="RAG_task_summerizer",
#     llm_config={
#         **base_config,
#         "functions": [_def_qa_summerize],
#     },
#     function_map={
#         "qa_summerize": qa_summerize,
#     },
#     code_execution_config=False,
#     is_termination_msg=is_termination_msg,
#     system_message=SUMMERIZER_PROMPT,
# )

