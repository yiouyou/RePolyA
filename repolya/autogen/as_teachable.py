from repolya._const import AUTOGEN_CONFIG
from repolya._log import logger_autogen

from autogen.agentchat.contrib.teachable_agent import TeachableAgent
from autogen import (
    AssistantAgent,
    UserProxyAgent,
    config_list_from_json,
)


config_list = config_list_from_json(env_or_file=str(AUTOGEN_CONFIG))


# Base Configuration
base_config = {
    "config_list": config_list,
    "request_timeout": 300,
    "temperature": 0,
    "model": "gpt-4",
    # "use_cache": False,
    "seed": 42,
}


teach_config={
    "verbosity": 0,  # 0 for basic info, 1 to add memory operations, 2 for analyzer messages, 3 for memo lists.
    "reset_db": True,  # Set to True to start over with an empty database.
    "path_to_db_dir": "./tmp/notebook/teachable_agent_db",  # Path to the directory where the database will be stored.
    "recall_threshold": 1.5,  # Higher numbers allow more (but less relevant) memos to be recalled.
}


##### teachable agent
TEACHABLE_user = UserProxyAgent(
    name="TEACHABLE_user",
    human_input_mode="NEVER",
    is_termination_msg=lambda x: True if "TERMINATE" in x.get("content") else False,
    max_consecutive_auto_reply=0,
)

TEACHABLE_agent = TeachableAgent(
    name="TEACHABLE_agent",
    llm_config=base_config,
    teach_config=teach_config
)

