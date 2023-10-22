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


config_list = config_list_from_json(env_or_file=str(AUTOGEN_CONFIG))
is_termination_msg = lambda x: isinstance(x, dict) and "TERMINATE" == str(x.get("content", ""))[-9:].upper()
# lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE")
# lambda x: True if "TERMINATE" in x.get("content") else False


# Base Configuration
base_config = {
    "config_list": config_list,
    "request_timeout": 120,
    "temperature": 0,
    "model": "gpt-4",
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

