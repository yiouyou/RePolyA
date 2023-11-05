from repolya._const import WORKSPACE_AUTOGEN
from repolya.autogen.organizer import (
    Organizer,
    ConversationResult,
)

def do_multi_search(msg):
    _agents = [
    ]
    _out = str(WORKSPACE_AUTOGEN / "organizer_output.txt")
    def validate_results_func():
        with open(_out, "r") as f:
            content = f.read()
        return bool(content)
    _organizer = Organizer(
        name="Search Team",
        agents=_agents,
        validate_results_func=validate_results_func,
    )
    _organizer_conversation_result = _organizer.broadcast_conversation(msg)
    match _organizer_conversation_result:
        case ConversationResult(success=True, cost=_cost, tokens=_tokens):
            print(f"✅ Organizer.Broadcast was successful. Team: {_organizer.name}")
            print(f"📊 Name: {_organizer.name} Cost: {_cost}, tokens: {_tokens}")
            with open(_out, "r") as f:
                content = f.read()
            return content
        case _:
            print(f"❌ Organizer.Broadcast failed. Team: {_organizer.name}")


def generate_search_query_for_event(_event: str) -> list[str]:
    _query = []
    return _query

def generate_vdb_for_search_query(_query: list[str], _vdb_name: str):
    pass

def generate_event_context(_evnet: str, _vdb_name: str) -> str:
    _context = "【context】"
    return _context

def generate_event_plan(_event: str, _vdb_name: str, _context:str) -> str:
    _plan = f"{_context}\n\n【plan】"
    return _plan

