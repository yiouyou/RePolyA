from repolya._const import AUTOGEN_CONFIG
from repolya._log import logger_autogen

from repolya.autogen.tool_function import (
    search,
    scrape,
    _def_search,
    _def_scrape,
)

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


is_termination_msg = lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE")


##### RD
RD_user = UserProxyAgent(
    name="RD_user",
    code_execution_config={
        "work_dir": 'rd',
        "last_n_messages": 3,
    },
    human_input_mode="TERMINATE",
    is_termination_msg=is_termination_msg,
)


RESEARCHER_PROMPT = "Research about a given query, collect as many information as possible, and generate detailed research results with loads of technique details with all reference links attached; Add TERMINATE to the end of the research report;"
RD_researcher = AssistantAgent(
    name="RD_researcher",
    llm_config={
        **base_config,
        "functions": [
            _def_search,
            _def_scrape,
        ],
    },
    function_map={
        "search": search,
        "scrape": scrape,
    },
    system_message=RESEARCHER_PROMPT,
)

