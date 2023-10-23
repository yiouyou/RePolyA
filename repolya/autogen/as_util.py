from repolya._const import AUTOGEN_CONFIG
from repolya._log import logger_autogen

from repolya.autogen.tool_function import (
    write_file,
    write_json_file,
    write_yaml_file,
    _def_write_file,
    _def_write_json_file,
    _def_write_yaml_file,
)

from autogen import(
    UserProxyAgent,
    AssistantAgent,
    config_list_from_json,
)


config_list = config_list_from_json(env_or_file=str(AUTOGEN_CONFIG))


# Base Configuration
base_config = {
    "config_list": config_list,
    "request_timeout": 120,
    "temperature": 0,
    "model": "gpt-3.5-turbo",
    # "use_cache": False,
    "seed": 42,
}


# text report analyst - writes a summary report of the results and saves them to a local text file
TEXT_PROMPT = "Text File Report Analyst. You exclusively use the write_file function on a summarized report."
text_report_analyst = AssistantAgent(
    name="Text_Report_Analyst",
    human_input_mode="NEVER",
    llm_config={
        **base_config,
        "functions": [_def_write_file],
    },
    function_map={
        "write_file": write_file,
    },
    system_message=TEXT_PROMPT,
)


# json report analyst - writes a summary report of the results and saves them to a local json file
JSON_PROMPT = "Json Report Analyst. You exclusively use the write_json_file function on the report."
json_report_analyst = AssistantAgent(
    name="Json_Report_Analyst",
    human_input_mode="NEVER",
    llm_config={
        **base_config,
        "functions": [_def_write_json_file],
    },
    function_map={
        "write_json_file": write_json_file,
    },
    system_message=JSON_PROMPT,
)


# yaml report analyst - writes a summary report of the results and saves them to a local yaml file
YML_PROMPT = "Yaml Report Analyst. You exclusively use the write_yml_file function on the report."
yaml_report_analyst = AssistantAgent(
    name="Yml_Report_Analyst",
    human_input_mode="NEVER",
    llm_config={
        **base_config,
        "functions": [_def_write_yaml_file],
    },
    function_map={
        "write_yaml_file": write_yaml_file,
    },
    system_message=YML_PROMPT,
)

