from repolya._const import AUTOGEN_CONFIG
from repolya._log import logger_autogen

from repolya.autogen.tool import rd_functions

from autogen import (
    AssistantAgent,
    UserProxyAgent,
    config_list_from_json,
)


config_list = config_list_from_json(env_or_file=str(AUTOGEN_CONFIG))

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

RD_researcher = AssistantAgent(
    name="RD_researcher",
    llm_config={
        "config_list": config_list,
        "functions": rd_functions,
    },
    system_message="Research about a given query, collect as many information as possible, and generate detailed research results with loads of technique details with all reference links attached; Add TERMINATE to the end of the research report;",
)

