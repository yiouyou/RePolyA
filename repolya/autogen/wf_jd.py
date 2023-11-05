from repolya._const import WORKSPACE_AUTOGEN, AUTOGEN_JD
from repolya._log import logger_yj

from repolya.autogen.organizer import (
    Organizer,
    ConversationResult,
)

from langchain.chat_models import ChatOpenAI
from langchain.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
)
from langchain.schema import StrOutputParser
from langchain.callbacks import get_openai_callback
from langchain.document_loaders import WebBaseLoader

from repolya.toolset.tool_langchain import (
    bing,
    ddg,
    google,
)
from repolya.rag.doc_loader import clean_txt
from repolya.rag.digest_dir import (
    calculate_md5,
    dir_to_faiss_openai,
)
from repolya.rag.digest_urls import urls_to_faiss

import shutil
import re
import os


def clean_filename(text, max_length=10):
    # 移除非法文件名字符（例如: \ / : * ? " < > |）
    clean_text = re.sub(r'[\\/*?:"<>|]', '', text)
    # 替换操作系统敏感的字符
    clean_text = clean_text.replace(' ', '_')  # 替换空格为下划线
    # 取前 max_length 个字符作为文件名
    return clean_text[:max_length]


def search_all(_query):
    _all = []
    # _all.extend(bing(_query))
    _all.extend(ddg(_query))
    # _all.extend(google(_query))
    return _all


def print_search_all(_all):
    _str = []
    for i in _all:
        _str.append(f"{i['link']}\n{i['title']}")
        # _str.append(f"{i['link']}\n{i['title']}\n{i['snippet']}")
    return "\n" + "\n".join(_str)


def fetch_all_link(_all, _event_dir):
    _txt_fp = []
    _all_link = [i['link'] for i in _all]
    _all_title = [i['title'] for i in _all]
    # print(_all_link)
    loader = WebBaseLoader()
    _re = loader.scrape_all(_all_link)
    for i in range(len(_re)):
        _fn = clean_filename(_all_title[i])
        _fp = os.path.join(_event_dir, f"{_fn}.txt")
        with open(_fp, "w") as wf:
            # _txt = _re[i].get_text()
            _txt = _re[i].get_text()
            wf.write(_txt)
        logger_yj.info(f"{_all_link[i]} -> {_fn}.txt")
        _txt_fp.append(_fp)
    return _txt_fp


def handle_fetch(_event_dir, _db_name, _clean_txt_dir):
    logger_yj.info(f"generate faiss_openai：开始")
    dir_to_faiss_openai(_event_dir, _db_name, _clean_txt_dir)
    logger_yj.info(f"generate faiss_openai：{_db_name}")
    logger_yj.info(f"generate faiss_openai：完成")


def task_with_context_template(_task, _context, template):
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    prompt = PromptTemplate.from_template(template)
    with get_openai_callback() as cb:
        chain = prompt | llm | StrOutputParser()
        _ans = chain.invoke({"_task": _task, "_context": _context})
        _token_cost = f"Tokens: {cb.total_tokens} = (Prompt {cb.prompt_tokens} + Completion {cb.completion_tokens}) Cost: ${format(cb.total_cost, '.5f')}"
    return [_ans, _token_cost]


gsqfe_template ="""假定你是领导秘书，需要针对下面的专题，利用搜索引擎收集相关信息：
# 专题
{_context}

针对应急事件，通常需掌握事件各阶段的基本概况、整体处置过程、相关成效、后续影响及对该事件的深入反思。

{_task}:
"""
def generate_search_query_for_event(_event: str) -> list[str]:
    logger_yj.info("generate_search_query_for_event：开始")
    _query = []
    _task = "请充分利用你的信息搜集专业能力和搜索引擎使用技巧，列出满足上面需求的搜索条目（仅输出条目列表，无任何其他）"
    _ans, _tc = task_with_context_template(_task, _event, gsqfe_template)
    _extracted = [re.sub(r'^\d+\.\s+', '', line) for line in _ans.strip().splitlines()]
    logger_yj.info(f"\n{_extracted}")
    logger_yj.info(_tc)
    _query = _extracted
    logger_yj.info("generate_search_query_for_event：完成")
    return _query


def generate_vdb_for_search_query(_query: list[str], _event_name: str):
    _event_dir = str(AUTOGEN_JD / _event_name)
    if not os.path.exists(_event_dir):
        os.makedirs(_event_dir)
        _db_name = str(AUTOGEN_JD / _event_dir / f"yj_rag_openai")
        _clean_txt_dir = str(AUTOGEN_JD / _event_dir / f"yj_rag_clean_txt")
        logger_yj.info("generate_vdb_for_search_query：开始")
        # ### search, fetch, vdb
        # for i in _query:
        #     i_all = search_all(i)
        #     i_psa = print_search_all(i_all)
        #     logger_yj.info(f"'{i}'")
        #     logger_yj.info(i_psa)
        #     fetch_all_link(i_all, _event_dir)
        # handle_fetch(_event_dir, _db_name, _clean_txt_dir)
        ### search, load, vdb
        _all = []
        for i in _query:
            i_all = search_all(i)
            _all.extend(i_all)
        _psa = print_search_all(_all)
        logger_yj.info(_psa)
        _all_link = [i['link'] for i in _all]
        urls_to_faiss(_all_link, _db_name, _clean_txt_dir)
        logger_yj.info("generate_vdb_for_search_query：完成")
    else:
        logger_yj.info(f"专题：'{_event_name}' 已存在")
        # shutil.rmtree(_event_dir)
        # os.makedirs(_event_dir)


def generate_event_context(_evnet: str, _event_name: str) -> str:
    _db_name = str(AUTOGEN_JD / _event_name / f"yj_rag_openai")
    logger_yj.info("generate_event_context：开始")
    _context = "【context】"
    logger_yj.info("generate_event_context：完成")
    return _context


def generate_event_plan(_event: str, _event_dir: str, _context:str) -> str:
    _db_name = str(AUTOGEN_JD / _event_dir / f"yj_rag_openai")
    logger_yj.info("generate_event_plan：开始")
    _plan = f"{_context}\n\n【plan】"
    logger_yj.info("generate_event_plan：完成")
    return _plan


# def do_multi_search(msg):
#     _agents = [
#     ]
#     _out = str(WORKSPACE_AUTOGEN / "organizer_output.txt")
#     def validate_results_func():
#         with open(_out, "r") as f:
#             content = f.read()
#         return bool(content)
#     _organizer = Organizer(
#         name="Search Team",
#         agents=_agents,
#         validate_results_func=validate_results_func,
#     )
#     _organizer_conversation_result = _organizer.broadcast_conversation(msg)
#     match _organizer_conversation_result:
#         case ConversationResult(success=True, cost=_cost, tokens=_tokens):
#             print(f"✅ Organizer.Broadcast was successful. Team: {_organizer.name}")
#             print(f"📊 Name: {_organizer.name} Cost: {_cost}, tokens: {_tokens}")
#             with open(_out, "r") as f:
#                 content = f.read()
#             return content
#         case _:
#             print(f"❌ Organizer.Broadcast failed. Team: {_organizer.name}")

