import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.append(_RePolyA)

from repolya.autogen.workflow import do_write_book
from repolya.autogen.util import cost_usage
from autogen import ChatCompletion


ChatCompletion.start_logging(reset_counter=True, compact=False)


_task='''write a book an space exploration for all age groups.'''
re = do_write_book(_task)
print(f"out: '{re}'")
print(f"cost_usage: {cost_usage(ChatCompletion.logged_history)}")

