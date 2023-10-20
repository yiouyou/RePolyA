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


##### write book (WB)
USER_PROMPT = "A human user. Interact with the planner to discuss the book concept and structure. The book writing needs to be approved by this user."
WB_user = UserProxyAgent(
    name="WB_user",
    code_execution_config=False,
    system_message=USER_PROMPT,
)


EXECUTOR_PROMPT = "Executor. Execute the code written by the author to write the contents of the book into files. Report the result if there is any error or if the taks is completed."
WB_executor = UserProxyAgent(
    name="WB_executor",
    code_execution_config={
        "work_dir": 'book',
        "last_n_messages": 3,
        "use_docker": False,
    },
    human_input_mode="NEVER",
    system_message=EXECUTOR_PROMPT,
)


AUTHOR_PROMPT = "Author. You follow an approved plan. You write book chapters according to the plan. The user can't modify your content directly. So do not suggest incomplete chapters chich requires others to modify. Don't include multiple chapters in one response. Don't ask others to copy and paste the content. Suggest the full content instead of partial content or content changes. If the content is not up to mark, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try. Always write the book content as python code which is ready to write the content to file."
WB_author = AssistantAgent(
    name="WB_author",
    llm_config=base_config,
    system_message=AUTHOR_PROMPT,
)


PLANNER_PROMPT = "Planner. Suggest a plan. Revise the plan based on feedback from user and critic, until user approval. The plan may involve a author who writes the book content within a python script which is ready to write the content to file and a editor who reviews the content written by the author and provides feedback. Executor will execute the code written by the author to write the contents of the book into files."
WB_planner = AssistantAgent(
    name="WB_planner",
    llm_config=base_config,
    system_message=PLANNER_PROMPT,
)


EDITOR_PROMPT = "Editor. Review the content written by the book writer and provide feedback."
WB_editor = AssistantAgent(
    name="WB_editor",
    llm_config=base_config,
    system_message=EDITOR_PROMPT,
)


CRITIC_PROMPT = "Critic. Double check plan, claims and content. Author will write the book content as python code which is ready to write the content to file. Provide feedback on the content and the plan."
WB_critic = AssistantAgent(
    name="WB_critic",
    llm_config=base_config,
    system_message=CRITIC_PROMPT,
)

