from repolya._const import AUTOGEN_CONFIG, AUTOGEN_DOC, AUTOGEN_REF
from repolya.autogen.agent import A_user, A_assist
from repolya.autogen.agent import CODE_user, CODE_pm, CODE_coder
from repolya.autogen.agent import RD_user, RD_researcher
from repolya.autogen.agent import MATH_user, MATH_assist
from repolya.autogen.agent import PLAN_TASK_user, PLAN_TASK_assist
from repolya.autogen.agent import RES_user, RES_engineer, RES_scientist, RES_planner, RES_executor, RES_critic
from repolya.autogen.agent import RAG_CODE_user, RAG_DOC_user, RAG_assist
from repolya.autogen.tool import search, scrape, planner

from autogen import (
    GroupChat,
    GroupChatManager,
    config_list_from_json
)

config_list = config_list_from_json(env_or_file=str(AUTOGEN_CONFIG))


def do_simple_task(msg):
    A_assist.reset()
    A_user.initiate_chat(
        A_assist,
        message=msg,
        clear_history=False,
    )
    return A_user.last_message()["content"]


def do_simple_code(msg):
    groupchat = GroupChat(
        agents=[
            CODE_user,
            CODE_coder,
            CODE_pm
        ],
        messages=[],
        max_round=12,
    )
    manager = GroupChatManager(
        name="CODE_GroupChatManager",
        groupchat=groupchat,
        llm_config={
            "config_list": config_list,
            "request_timeout": 120,
            "seed": 42,
        }
    )
    CODE_user.initiate_chat(
        manager,
        message=msg,
    )
    return CODE_user.last_message()["content"]


def do_rd(msg):
    RD_user.register_function(
        function_map={
            "search": search,
            "scrape": scrape,
        }
    )
    RD_researcher.reset()
    RD_user.initiate_chat(
        RD_researcher,
        message=msg
    )
    RD_user.stop_reply_at_receive(RD_researcher)
    RD_user.send(
        recipient=RD_researcher,
        message="Give me the research report that just generated again, return ONLY the report & reference links",
    )
    return RD_user.last_message()["content"]


def do_math(msg):
    MATH_assist.reset()
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
    PLAN_TASK_assist.reset()
    PLAN_TASK_user.initiate_chat(
        PLAN_TASK_assist,
        message=msg
    )
    return PLAN_TASK_user.last_message()["content"]


def do_res(msg):
    groupchat = GroupChat(
        agents=[
            RES_user,
            RES_engineer,
            RES_scientist,
            RES_planner,
            RES_executor,
            RES_critic
        ],
        messages=[],
        max_round=50
    )
    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config={
            "config_list": config_list,
            "request_timeout": 120,
            "seed": 42,
            "temperature": 0,
            "model": "gpt-4",
        },
    )
    RES_user.initiate_chat(
        manager,
        message=msg,
    )
    return RES_user.last_message()["content"]


def do_rag_doc(msg, search_string, docs_path, collection_name):
    _RAG_DOC_user = RAG_DOC_user(
        docs_path,
        'gpt-3.5-turbo-16k',
        collection_name,
    )
    RAG_assist.reset()
    _RAG_DOC_user.initiate_chat(
        RAG_assist,
        problem=msg,
        n_results=10,
        search_string=search_string,
    )
    return _RAG_DOC_user.last_message()["content"]


def do_rag_code(msg, search_string, docs_path, collection_name):
    _RAG_CODE_user = RAG_CODE_user(
        docs_path,
        'gpt-4',
        collection_name,
    )
    RAG_assist.reset()
    _RAG_CODE_user.initiate_chat(
        RAG_assist,
        problem=msg,
        n_results=10,
        search_string=search_string,
    )
    return _RAG_CODE_user.last_message()["content"]


# print(autogen.ChatCompletion.logged_history)

