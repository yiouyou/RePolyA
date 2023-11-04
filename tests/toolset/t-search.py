import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.append(_RePolyA)

from repolya._const import WORKSPACE_TOOLSET
from repolya._log import logger_toolset

from repolya.toolset.tool_langchain import (
    bing,
    ddg,
    google,
)

from pprint import pprint

_query = sys.argv[1]


def search_all(_query):
    _re = []
    _re.extend(bing(_query))
    _re.extend(ddg(_query))
    _re.extend(google(_query))
    return _re

def print_search_all(_all):
    _str = []
    for _i in _all:
        _str.append(f"{_i['link']}\n{_i['title']}\n{_i['snippet']}")
    return "\n\n".join(_str)

print(print_search_all(search_all(_query)))


# pprint(bing(_query))
# pprint(ddg(_query))
# pprint(google(_query))

