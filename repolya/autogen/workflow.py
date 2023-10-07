from repolya._const import AUTOGEN_CONFIG
from repolya.autogen.agent import RD_user, RD_researcher
from repolya.autogen.agent import A_user, A_assist
from repolya.autogen.agent import CODE_user, CODE_pm, CODE_coder
from repolya.autogen.tool import search, scrape

from autogen import (
    GroupChat,
    GroupChatManager,
    config_list_from_json
)

config_list = config_list_from_json(env_or_file=str(AUTOGEN_CONFIG))


def do_simple_ask(query):
    A_user.initiate_chat(
        A_assist,
        message=query,
    )
    return A_user.last_message()["content"]


def do_simple_code(query):
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
        message=query,
    )
    return CODE_user.last_message()["content"]


def do_research(query):
    RD_user.register_function(
        function_map={
            "search": search,
            "scrape": scrape,
        }
    )
    RD_user.initiate_chat(RD_researcher, message=query)
    RD_user.stop_reply_at_receive(RD_researcher)
    RD_user.send(
        "Give me the research report that just generated again, return ONLY the report & reference links",
        RD_researcher
    )
    return RD_user.last_message()["content"]

