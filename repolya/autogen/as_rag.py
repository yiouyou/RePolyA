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

gpt4_config = {
    "config_list": config_list,
    "model": "gpt-4",
    "temperature": 0,
    "request_timeout": 120,
    "seed": 42,
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
    name="RAG_CODE_assist",
    llm_config=gpt4_config,
    system_message="You are a helpful assistant.",
)

