from repolya._const import AUTOGEN_CONFIG
from repolya._log import logger_autogen

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


is_termination_msg = lambda x: True if "TERMINATE" in x.get("content") else False


##### CODE
USER_PROMPT = "A human admin. You will give the idea, run the code provided by engineer and save the code to disk. Don't run the test code provided by QA."
CODE_user = UserProxyAgent(
    name="CODE_user",
    code_execution_config={
        "work_dir": 'code',
        "use_docker": False,
        "last_n_messages": 3,
    },
    human_input_mode="NEVER", # "ALWAYS",
    max_consecutive_auto_reply=10,
    system_message=USER_PROMPT,
)

CODE_engineer = AssistantAgent(
    name="CODE_engineer",
    is_termination_msg=is_termination_msg,
    llm_config=base_config,
)


QA_PROMPT = "Quality Assurance. You will write comprehensive and robust tests to ensure codes will work as expected without bugs. The test code you write should conform to code standard like PEP8, be modular, easy to read and maintain, and use 'unittest' module. If you want the user to save the code in a file before executing it, put # filename: <filename> inside the code block as the first line. Reply 'TERMINATE' in the end when everything is done."
CODE_qa = AssistantAgent(
    name="CODE_qa",
    llm_config=base_config,
    is_termination_msg=is_termination_msg,
    system_message=QA_PROMPT,
)


PM_PROMPT = "Product Manager. You will help break down the initial idea into a well scoped requirement for the engineer. Don't involve in future conversations or error fixing."
CODE_pm = AssistantAgent(
    name="CODE_pm",
    llm_config=base_config,
    is_termination_msg=is_termination_msg,
    system_message=PM_PROMPT,
)

