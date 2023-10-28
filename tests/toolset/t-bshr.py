import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.append(_RePolyA)

from repolya._const import WORKSPACE_TOOLSET
from repolya._log import logger_toolset
from repolya.toolset.tool_bshr import run_bshr


_re, _token_cost = run_bshr('What is at the bottom of the deepest part of the deepest ocean?')
print(_re)
print(_token_cost)

