from repolya._const import AUTOGEN_CONFIG
from repolya._log import logger_autogen

from repolya.autogen.db_postgre import (
    PostgresManager,
    PostgresAgentInstruments,
)
from repolya.autogen.tool_function import (
    _def_run_postgre,
)
from repolya.autogen.as_util import (
    text_report_analyst,
    json_report_analyst,
    yaml_report_analyst,
)
from repolya.autogen.organizer import (
    Organizer,
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
    "model": "gpt-4",
    # "use_cache": False,
    "seed": 42,
}


def is_termination_msg(content):
    have_content = content.get("content", None) is not None
    if have_content and "APPROVED" in content["content"]:
        return True
    return False

COMPLETION_PROMPT = "If everything looks good, respond with 'APPROVED'."


# takes in the prompt and manages the group chat
USER_PROMPT = (
    "A human admin. Interact with the Product Manager to discuss the plan. Plan execution needs to be approved by this admin."
    # "A human admin. Interact with the Product Manager to discuss the plan. Plan execution needs to be approved by this admin. " + COMPLETION_PROMPT
)
POSTGRE_user = UserProxyAgent(
    name="POSTGRE_user",
    code_execution_config=False,
    human_input_mode="NEVER",
    is_termination_msg=is_termination_msg,
    system_message=USER_PROMPT,
)


# generates the sql query
ENGINEER_PROMPT = (
    "A Data Engineer. Generate the initial SQL based on the requirements provided. Send it to the Sr Data Analyst to be executed."
    # "A Data Engineer. You follow an approved plan. Generate the initial SQL based on the requirements provided. Send it to the Sr Data Analyst for review. " + COMPLETION_PROMPT
)
POSTGRE_engineer = AssistantAgent(
    name="POSTGRE_engineer",
    code_execution_config=False,
    human_input_mode="NEVER",
    is_termination_msg=is_termination_msg,
    llm_config=base_config,
    system_message=ENGINEER_PROMPT,
)


# run the sql query and generate the response
ANALYST_PROMPT = (
    "Sr Data Analyst. You run the SQL query using the run_postgre function, send the raw response to the data viz team. You use the run_postgre function" + " to generate the response and send it to the product manager for final review."
    # "Sr Data Analyst. You follow an approved plan. You run the SQL query, generate the response and send it to the product manager for final review. " + COMPLETION_PROMPT
)
# POSTGRE_analyst = AssistantAgent(
#     name="POSTGRE_analyst",
#     code_execution_config=False,
#     human_input_mode="NEVER",
#     is_termination_msg=is_termination_msg,
#     llm_config={
#         **base_config,
#         "functions": [_def_run_postgre],
#     },
#     function_map={
#         'run_postgre': run_postgre,
#     },
#     system_message=ANALYST_PROMPT,
# )
def build_sr_data_analyst_agent(db: PostgresManager):
    return AssistantAgent(
        name="POSTGRE_analyst",
        code_execution_config=False,
        human_input_mode="NEVER",
        is_termination_msg=is_termination_msg,
        llm_config={
            **base_config,
            "functions": [_def_run_postgre],
        },
        function_map={
            'run_postgre': db.run_postgre,
        },
        system_message=ANALYST_PROMPT,
    )


# validate the response to make sure it's correct
PM_PROMPT = (
    "Product Manager. Validate the response to make sure it's correct. " + COMPLETION_PROMPT
)
POSTGRE_pm = AssistantAgent(
    name="POSTGRE_manager",
    code_execution_config=False,
    human_input_mode="NEVER",
    is_termination_msg=is_termination_msg,
    llm_config=base_config,
    system_message=PM_PROMPT,
)


def build_data_eng_team(agent_instruments: PostgresAgentInstruments):
    # create a set of agents with specific roles
    # admin user proxy agent - takes in the prompt and manages the group chat
    POSTGRE_user = UserProxyAgent(
        name="Admin",
        code_execution_config=False,
        human_input_mode="NEVER",
        system_message=USER_PROMPT,
    )

    # data engineer agent - generates the sql query
    POSTGRE_engineer = AssistantAgent(
        name="Engineer",
        code_execution_config=False,
        human_input_mode="NEVER",
        llm_config=base_config,
        system_message=ENGINEER_PROMPT,
    )

    POSTGRE_analyst = AssistantAgent(
        name="Sr_Data_Analyst",
        code_execution_config=False,
        human_input_mode="NEVER",
        llm_config={
            **base_config,
            "functions": [_def_run_postgre],
        },
        function_map={
            'run_postgre': agent_instruments.run_postgre,
        },
        system_message=ANALYST_PROMPT,
    )

    # product manager – validate the response to make sure it's correct
    POSTGRE_pm = AssistantAgent(
        name="Product_Manager",
        code_execution_config=False,
        human_input_mode="NEVER",
        llm_config=base_config,
        system_message=PM_PROMPT,
    )


def build_team_organizer(
    team: str,
    agent_instruments: PostgresAgentInstruments,
    # db: PostgresManager,
    validate_results_func: callable = None
) -> Organizer:
    if team == "data_eng":
        return Organizer(
            name="Postgres Data Analytics Multi-Agent ::: Data Engineering Team",
            # agents=[
            #     POSTGRE_user,
            #     POSTGRE_engineer,
            #     build_sr_data_analyst_agent(db),
            #     # POSTGRE_pm,
            # ],
            agents=build_data_eng_team(agent_instruments),
            agent_instruments=agent_instruments,
            validate_results_func=validate_results_func,
        )
    # elif team == "data_viz":
    #     return Organizer(
    #         name="Postgres Data Analytics Multi-Agent ::: Data Viz Team",
    #         # agents=[
    #         #     POSTGRE_user,
    #         #     text_report_analyst,
    #         #     json_report_analyst,
    #         #     yaml_report_analyst,
    #         # ],
    #         agents=build_data_viz_team(agent_instruments),
    #         validate_results_func=validate_results_func,
    #     )
    raise Exception("Unknown team: " + team)

