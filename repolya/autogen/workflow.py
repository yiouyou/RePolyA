from repolya._const import AUTOGEN_CONFIG, WORKSPACE_RAG, WORKSPACE_AUTOGEN
from repolya._log import logger_autogen, logger_rag

from repolya.autogen.as_basic import A_user, A_assist
from repolya.autogen.as_teachable import TEACHABLE_user, TEACHABLE_agent
from repolya.autogen.as_book import WB_user, WB_executor, WB_author, WB_planner, WB_editor, WB_critic
from repolya.autogen.as_code import CODE_user, CODE_pm, CODE_engineer, CODE_qa
from repolya.autogen.as_math import MATH_user, MATH_assist
from repolya.autogen.as_plantask import PLAN_TASK_user, PLAN_TASK_assist
from repolya.autogen.as_rag import (
    RAG_CODE_user, RAG_DOC_user, RAG_assist,
    RAG_boss, RAG_boss_aid, RAG_pm, RAG_engineer, RAG_reviewer,
    RAG_task_user, RAG_task_planner, RAG_task_critic,
    RAG_task_user_zh, RAG_task_planner_zh, RAG_task_critic_zh,
)
from repolya.autogen.as_jdml import (
    JDML_task_user_zh, JDML_task_planner_zh, JDML_task_critic_zh,
)
from repolya.autogen.as_rd import RD_user, RD_researcher
from repolya.autogen.as_research import RES_user, RES_engineer, RES_scientist, RES_planner, RES_executor, RES_critic
from repolya.autogen.as_draw import DRAW_user, DRAW_artist, DRAW_critic
from repolya.autogen.as_postgre import (
    # POSTGRE_user,
    # POSTGRE_engineer,
    # POSTGRE_pm,
    # build_sr_data_analyst_agent,
    build_team_organizer,
)
from repolya.autogen.as_util import text_report_analyst, json_report_analyst, yaml_report_analyst
from repolya.autogen.db_postgre import (
    PostgresManager,
    DatabaseEmbedder,
    PostgresAgentInstruments,
)
from repolya.autogen.organizer import (
    Organizer,
    add_cap_ref,
    generate_session_id,
    ConversationResult,
)
from autogen import (
    GroupChat,
    GroupChatManager,
    config_list_from_json,
)

from repolya.rag.vdb_faiss import (
    get_faiss_OpenAI,
    get_faiss_HuggingFace,
)
from repolya.rag.qa_chain import (
    qa_vdb_multi_query,
    qa_vdb_multi_query_textgen,
    qa_docs_ensemble_query,
    qa_docs_parent_query,
    qa_summerize,
    summerize_text,
)
from repolya.rag.doc_loader import clean_txt
from repolya.toolset.util import calc_token_cost

import os
import re
import time


config_list = config_list_from_json(env_or_file=str(AUTOGEN_CONFIG))


# Base Configuration
base_config = {
    "config_list": config_list,
    "request_timeout": 300,
    "temperature": 0,
    "model": "gpt-3.5-turbo",
    "use_cache": False,
    # "seed": 42,
}


def do_math(msg):
    MATH_assist.reset()
    MATH_user.initiate_chat(
        MATH_assist,
        problem=msg,
        prompt_type="two_tools"
    )
    return MATH_user.last_message()["content"]


def do_simple_task(msg):
    A_assist.reset()
    A_user.initiate_chat(
        A_assist,
        message=msg,
        clear_history=False,
    )
    return A_user.last_message()["content"]


def do_teachable(msg):
    TEACHABLE_user.initiate_chat(
        TEACHABLE_agent,
        message=msg,
        clear_history=False,
    )
    # teachable_agent.learn_from_user_feedback()
    return TEACHABLE_user.last_message()["content"]


def do_plan_task(msg):
    PLAN_TASK_assist.reset()
    PLAN_TASK_user.initiate_chat(
        PLAN_TASK_assist,
        message=msg
    )
    return PLAN_TASK_user.last_message()["content"]


def do_simple_code(msg):
    groupchat = GroupChat(
        agents=[
            CODE_user,
            CODE_engineer,
            CODE_pm,
        ],
        messages=[],
        max_round=10,
    )
    manager = GroupChatManager(
        name="CODE_GroupChatManager",
        groupchat=groupchat,
        llm_config=base_config,
    )
    CODE_user.initiate_chat(
        manager,
        message=msg,
        clear_history=False,
    )
    return CODE_user.last_message()["content"]


def do_simple_code_qa(msg):
    groupchat = GroupChat(
        agents=[
            CODE_user,
            CODE_engineer,
            CODE_qa,
            CODE_pm,
        ],
        messages=[],
        max_round=20,
    )
    manager = GroupChatManager(
        name="CODE_GroupChatManager",
        groupchat=groupchat,
        llm_config=base_config,
    )
    CODE_user.initiate_chat(
        manager,
        message=msg,
        clear_history=False,
    )
    return CODE_user.last_message()["content"]


def do_rd(msg):
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
        llm_config=base_config,
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


def create_rag_task_list(msg):
    _agents = [
        RAG_task_user,
        RAG_task_planner,
        RAG_task_critic,
        RAG_task_planner,
    ]
    _out = str(WORKSPACE_AUTOGEN / "organizer_output.txt")
    def validate_results_func():
        with open(_out, "r") as f:
            content = f.read()
        return bool(content)
    _organizer = Organizer(
        name="RAG Task Team",
        agents=_agents,
        validate_results_func=validate_results_func,
    )
    _organizer_conversation_result = _organizer.sequential_conversation(msg)
    match _organizer_conversation_result:
        case ConversationResult(success=True, cost=_cost, tokens=_tokens):
            print(f"✅ Organizer was successful. Team: {_organizer.name}")
            print(f"📊 Name: {_organizer.name} Cost: {_cost}, tokens: {_tokens}")
            with open(_out, "r") as f:
                content = f.read()
            return content
        case _:
            print(f"❌ Organizer failed. Team: {_organizer.name}")


def create_rag_task_list_zh(msg):
    _agents = [
        RAG_task_user_zh,
        RAG_task_planner_zh,
        RAG_task_critic_zh,
        RAG_task_planner_zh,
    ]
    _out = str(WORKSPACE_AUTOGEN / "organizer_output.txt")
    def validate_results_func():
        with open(_out, "r") as f:
            content = f.read()
        return bool(content)
    _organizer = Organizer(
        name="RAG Task Team",
        agents=_agents,
        validate_results_func=validate_results_func,
    )
    _organizer_conversation_result = _organizer.sequential_conversation(msg)
    match _organizer_conversation_result:
        case ConversationResult(success=True, cost=_cost, tokens=_tokens):
            print(f"✅ Organizer was successful. Team: {_organizer.name}")
            print(f"📊 Name: {_organizer.name} Cost: {_cost}, tokens: {_tokens}")
            _tk = int(_tokens/3)
            with open(_out, "r") as f:
                content = f.read()
            return content, f"Tokens: {_tokens} = (Prompt {_tokens - _tk} + Completion {_tk}) Cost: ${_cost}"
        case _:
            print(f"❌ Organizer failed. Team: {_organizer.name}")


def create_jdml_task_list_zh(msg):
    _agents = [
        JDML_task_user_zh,
        JDML_task_planner_zh,
        JDML_task_critic_zh,
        JDML_task_planner_zh,
    ]
    _out = str(WORKSPACE_AUTOGEN / "organizer_output.txt")
    def validate_results_func():
        with open(_out, "r") as f:
            content = f.read()
        return bool(content)
    _organizer = Organizer(
        name="JDML Task Team",
        agents=_agents,
        validate_results_func=validate_results_func,
    )
    _organizer_conversation_result = _organizer.sequential_conversation(msg)
    match _organizer_conversation_result:
        case ConversationResult(success=True, cost=_cost, tokens=_tokens):
            print(f"✅ Organizer was successful. Team: {_organizer.name}")
            print(f"📊 Name: {_organizer.name} Cost: {_cost}, tokens: {_tokens}")
            with open(_out, "r") as f:
                content = f.read()
            return content
        case _:
            print(f"❌ Organizer failed. Team: {_organizer.name}")
    # success, _messages = _organizer.sequential_conversation(msg)
    # # print(success)
    # # print(_messages)
    # _task_list = _messages[-1]
    # return _task_list


def search_faiss_openai(text, _vdb):
    _re = []
    questions = [re.sub(r"^\d+\.\s*", "", line) for line in text.split("\n") if re.match(r"^\d+\.", line)]
    _tc = []
    for i in questions:
        i_ans, i_step, i_token_cost = qa_vdb_multi_query(i, _vdb, 'stuff')
        i_ans = clean_txt(i_ans)
        _re.append(f"Q: {i}\nA: {i_ans}")
        _tc.append(i_token_cost)
    _token_cost = calc_token_cost(_tc)
    return '\n\n'.join(_re), _token_cost


def search_faiss_openai_textgen(text, _vdb, _textgen_url):
    _context, _token_cost = "", ""
    _re = []
    _list = text.split("\n")
    questions = []
    for i in _list:
        if re.match(r"^\d+\.", i):            
            questions.append(re.sub(r"^\d+\.\s*", "", i))
        else:
            questions.append(i)
    logger_rag.info(questions)
    for i in questions:
        i_ans, i_step, i_token_cost = qa_vdb_multi_query_textgen(i, _vdb, 'stuff', _textgen_url)
        i_ans = clean_txt(i_ans)
        # i_out = f"Q: {i}\nA: {i_ans}"
        i_out = f"{i_ans}"
        if i != i_ans:
            # logger_rag.info(i_out)
            _re.append(i_out)
    _context = '\n\n'.join(_re)
    logger_rag.info(f"context:\n'{_context}'")
    return _context, _token_cost


def do_rag_code_aid(msg, docs_path, collection_name):
    _RAG_boss_aid = RAG_boss_aid(
        docs_path,
        'gpt-4',
        collection_name,
    )
    _RAG_boss_aid.reset(),
    RAG_pm.reset(),
    RAG_engineer.reset(),
    RAG_reviewer.reset(),
    groupchat = GroupChat(
        agents=[
            _RAG_boss_aid,
            RAG_engineer,
            RAG_pm,
            RAG_reviewer,
        ],
        messages=[],
        max_round=12,
    )
    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config=base_config,
    )
    ### Start chatting with boss_aid as this is the user proxy agent
    _RAG_boss_aid.initiate_chat(
        manager,
        problem=msg,
        n_results=3,
    )


def do_rag_code_call_aid(msg, docs_path, collection_name):
    RAG_boss.reset(),
    RAG_pm.reset(),
    RAG_engineer.reset(),
    RAG_reviewer.reset(),
    _RAG_boss_aid = RAG_boss_aid(
        docs_path,
        'gpt-4',
        collection_name,
    )
    def retrieve_content(message):
        _RAG_boss_aid.n_results = 3  # Set the number of results to be retrieved.
        # Check if we need to update the context.
        update_context_case1, update_context_case2 = _RAG_boss_aid._check_update_context(message)
        if (update_context_case1 or update_context_case2) and _RAG_boss_aid.update_context:
            _RAG_boss_aid.problem = message if not hasattr(_RAG_boss_aid, "problem") else _RAG_boss_aid.problem
            _, ret_msg = _RAG_boss_aid._generate_retrieve_user_reply(message)
        else:
            ret_msg = _RAG_boss_aid.generate_init_message(message, n_results=3)
        return ret_msg if ret_msg else message
    _RAG_boss_aid.human_input_mode = "NEVER"
    llm_config = {
        **base_config,
        "functions": [
            {
                "name": "retrieve_content",
                "description": "retrieve content for code generation and question answering.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Refined message which keeps the original meaning and can be used to retrieve content for code generation and question answering.",
                        },
                    },
                    "required": ["message"],
                },
            },
        ],
    }
    for agent in [RAG_pm, RAG_engineer, RAG_reviewer]:
        # update llm_config for assistant agents.
        agent.llm_config.update(llm_config)
        agent.register_function(
            function_map={
                "retrieve_content": retrieve_content,
            }
        )
    groupchat = GroupChat(
        agents=[
            RAG_boss,
            RAG_engineer,
            RAG_pm,
            RAG_reviewer,
        ],
        messages=[],
        max_round=12,
    )
    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config=base_config,
    )
    ### Start chatting with boss_aid as this is the user proxy agent
    RAG_boss.initiate_chat(
        manager,
        message=msg,
    )


def do_write_book(msg):
    groupchat = GroupChat(
        agents=[
            WB_user,
            WB_executor,
            WB_author,
            WB_planner,
            WB_editor,
            WB_critic,
        ],
        messages=[],
        max_round=50,
    )
    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config=base_config,
    )
    WB_user.initiate_chat(
        manager,
        message=msg,
    )
    return WB_user.last_message()["content"]


def do_draw(msg):
    groupchat = GroupChat(
        agents=[
            DRAW_user,
            DRAW_artist,
            DRAW_critic,
        ],
        messages=[],
        max_round=50,
    )
    manager = GroupChatManager(
        groupchat=groupchat,
        llm_config={
            "config_list": config_list,
            "request_timeout": 120,
            "temperature": 0,
            "model": "gpt-3.5-turbo",
            "seed": 42,
        },
    )
    DRAW_user.initiate_chat(
        manager,
        message=msg,
    )
    return DRAW_user.last_message()["content"]


def do_postgre_organizer(msg):
    DB_URL = os.environ.get("POSTGRE_URL")
    POSTGRES_TABLE_DEFINITIONS_CAP_REF = "TABLE_DEFINITIONS"
    prompt = f"Fulfill this database query: {msg}. "
    session_id = generate_session_id(msg)
    with PostgresAgentInstruments(DB_URL, session_id) as (agent_instruments, db):
        # ----------- Gate Team: Prevent bad prompts from running and burning your $$$ -------------
        gate_organizer = build_team_organizer(
            "scrum_master",
            agent_instruments,
            validate_results=lambda: (True, ""),
        )
        gate_organizer: ConversationResult = (
            gate_organizer.sequential_conversation(prompt)
        )
        print("gate_organizer.last_message_str", gate_organizer.last_message_str)
        nlq_confidence = int(gate_organizer.last_message_str)
        match nlq_confidence:
            case (1 | 2):
                print(f"❌ Gate Team Rejected - Confidence too low: {nlq_confidence}")
                return
            case (3 | 4 | 5):
                print(f"✅ Gate Team Approved - Valid confidence: {nlq_confidence}")
            case _:
                print("❌ Gate Team Rejected - Invalid response")
                return
        # -------- BUILD TABLE DEFINITIONS -----------
        map_table_name_to_table_def = db.get_table_definition_map_for_embeddings()
        database_embedder = DatabaseEmbedder()
        for name, table_def in map_table_name_to_table_def.items():
            database_embedder.add_table(name, table_def)
        similar_tables = database_embedder.get_similar_tables(msg, n=5)

        table_definitions = database_embedder.get_table_definitions_from_names(
            similar_tables
        )
        related_table_names = db.get_related_tables(similar_tables, n=3)
        core_and_related_table_definitions = (
            database_embedder.get_table_definitions_from_names(
                related_table_names + similar_tables
            )
        )
        prompt = add_cap_ref(
            prompt,
            f"Use these {POSTGRES_TABLE_DEFINITIONS_CAP_REF} to satisfy the database query.",
            POSTGRES_TABLE_DEFINITIONS_CAP_REF,
            table_definitions,
        )
        # ----------- Data Eng Team: Based on a sql table definitions and a prompt create an sql statement and execute it -------------
        data_eng_organizer = build_team_organizer(
            "data_eng",
            agent_instruments,
            validate_results=agent_instruments.validate_run_postgre,
        )
        data_eng_conversation_result: ConversationResult = (
            data_eng_organizer.sequential_conversation(prompt)
        )
        match data_eng_conversation_result:
            case ConversationResult(
                success=True, cost=data_eng_cost, tokens=data_eng_tokens
            ):
                print(f"✅ Organizer was successful. Team: {data_eng_organizer.name}")
                print(f"📊 {data_eng_organizer.name} Cost: {data_eng_cost}, tokens: {data_eng_tokens}")
            case _:
                print(f"❌ Organizer failed. Team: {data_eng_organizer.name} Failed")
        # ----------- Data Insights Team: Based on sql table definitions and a prompt generate novel insights -------------
        innovation_prompt = f"Given this database query: '{msg}'. Generate novel insights and new database queries to give business insights."
        insights_prompt = add_cap_ref(
            innovation_prompt,
            f"Use these {POSTGRES_TABLE_DEFINITIONS_CAP_REF} to satisfy the database query.",
            POSTGRES_TABLE_DEFINITIONS_CAP_REF,
            core_and_related_table_definitions,
        )
        data_insights_organizer = build_team_organizer(
            "data_insights",
            agent_instruments,
            validate_results=agent_instruments.validate_innovation_files,
        )
        data_insights_conversation_result: ConversationResult = (
            data_insights_organizer.round_robin_conversation(
                insights_prompt, loops=1
            )
        )
        match data_insights_conversation_result:
            case ConversationResult(
                success=True, cost=data_insights_cost, tokens=data_insights_tokens
            ):
                print(f"✅ Organizer was successful. Team: {data_insights_organizer.name}")
                print(f"📊 {data_insights_organizer.name} Cost: {data_insights_cost}, tokens: {data_insights_tokens}")
            case _:
                print(f"❌ Organizer failed. Team: {data_insights_organizer.name} Failed")

