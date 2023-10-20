import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.append(_RePolyA)

from repolya.autogen.workflow import do_draw
from repolya.autogen.util import cost_usage
from autogen import ChatCompletion


ChatCompletion.start_logging(reset_counter=True, compact=False)


_task='''Generate a photo realistic image of llama driving a car.'''
re = do_draw(_task)
print(f"out: '{re}'")
print(f"cost_usage: {cost_usage(ChatCompletion.logged_history)}")

