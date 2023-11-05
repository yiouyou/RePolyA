from repolya._const import WORKSPACE_AUTOGEN
from repolya._log import logger_yj

from repolya.autogen.organizer import (
    Organizer,
    ConversationResult,
)


def search_all(_query):
    _re = []
    # _re.extend(bing(_query))
    _re.extend(ddg(_query))
    # _re.extend(google(_query))
    return _re

def print_search_all(_all):
    _str = []
    for i in _all:
        _str.append(f"{i['link']}\n{i['title']}\n{i['snippet']}")
    return "\n\n".join(_str)


def generate_search_query_for_event(_event: str) -> list[str]:
    logger_yj.info("generate_search_query_for_event: start")
    _query = []
    logger_yj.info("generate_search_query_for_event: done")
    return _query

def generate_vdb_for_search_query(_query: list[str], _vdb_name: str):
    logger_yj.info("generate_vdb_for_search_query: start")
    logger_yj.info("generate_vdb_for_search_query: done")

def generate_event_context(_evnet: str, _vdb_name: str) -> str:
    logger_yj.info("generate_event_context: start")
    _context = "【context】"
    logger_yj.info("generate_event_context: done")
    return _context

def generate_event_plan(_event: str, _vdb_name: str, _context:str) -> str:
    logger_yj.info("generate_event_plan: start")
    _plan = f"{_context}\n\n【plan】"
    logger_yj.info("generate_event_plan: done")
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

