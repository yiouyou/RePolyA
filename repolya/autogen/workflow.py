from repolya._const import AUTOGEN_CONFIG
from repolya.autogen.agent import A_user, A_assist
from repolya.autogen.agent import CODE_user, CODE_pm, CODE_coder
from repolya.autogen.agent import RD_user, RD_researcher
from repolya.autogen.agent import MATH_user, MATH_assist
from repolya.autogen.agent import PLAN_TASK_user, PLAN_TASK_assist
from repolya.autogen.tool import search, scrape, planner

from autogen import (
    GroupChat,
    GroupChatManager,
    config_list_from_json
)

config_list = config_list_from_json(env_or_file=str(AUTOGEN_CONFIG))


def do_simple_task(msg):
    A_user.initiate_chat(
        A_assist,
        message=msg,
        clear_history=False,
    )
    return A_user.last_message()["content"]


def do_simple_code(msg):
    groupchat = GroupChat(
        agents=[CODE_user, CODE_coder, CODE_pm],
        messages=[]
    )
    manager = GroupChatManager(
        name="CODE_GroupChatManager",
        groupchat=groupchat,
        llm_config={
            "request_timeout": 120,
            "seed": 42,
            "config_list": config_list,
        }
    )
    CODE_user.initiate_chat(
        manager,
        message=msg,
    )
    return CODE_user.last_message()["content"]


def do_research(msg):
    RD_user.register_function(
        function_map={
            "search": search,
            "scrape": scrape,
        }
    )
    RD_user.initiate_chat(
        RD_researcher,
        message=msg
    )
    RD_user.stop_reply_at_receive(RD_researcher)
    RD_user.send(
        "Give me the research report that just generated again, return ONLY the report & reference links",
        RD_researcher
    )
    return RD_user.last_message()["content"]


def do_math(msg):
    MATH_user.initiate_chat(
        MATH_assist,
        problem=msg,
        prompt_type="two_tools"
    )
    return MATH_user.last_message()["content"]


def do_plan_task(msg):
    PLAN_TASK_user.register_function(
        function_map={
            "planner": planner,
        }
    )
    PLAN_TASK_user.initiate_chat(
        PLAN_TASK_assist,
        message=msg
    )
    return PLAN_TASK_user.last_message()["content"]


