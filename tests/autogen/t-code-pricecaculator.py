import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.append(_RePolyA)

from repolya._const import WORKSPACE_AUTOGEN
from repolya.autogen.workflow import do_simple_code_qa
from repolya.autogen.util import cost_usage
from autogen import ChatCompletion


ChatCompletion.start_logging(reset_counter=True, compact=False)


_format = 'os-tier-type-unit'

_workspace = str(WORKSPACE_AUTOGEN)
_options = str(WORKSPACE_AUTOGEN / 'service_options')

_task = f'''
path of workspace: {_workspace}
In workspace, create the 'price_caculator.py' in which write three functions:
- def instance_caculator(instance_perhour:float) -> permonth_price:float # permonth_price = instance_perhour * 730
- def isolated_caculator(i1_instance_num:int, i2_instance_num:int, i3_instance_num:int, i1_instance_perhour:float, i2_instance_perhour:float, i3_instance_perhour:float, stamp_price:float) -> permonth_price:float # permonth_price = (i1_instance_perhour*i1_instance_num + i2_instance_perhour*i2_instance_num + i3_instance_perhour*i3_instance_num + stamp_price)*730
- def isolatedv2_caculator(Core_num:int, Core_perhour:float, common_price:float) -> permonth_price:float # permonth_price = (Core_num*Core_perhour + 2*common_price)*730

Remeber, save the code to disk.
'''

re = do_simple_code_qa(_task)
print(f"out: '{re}'")
print(f"cost_usage: {cost_usage(ChatCompletion.logged_history)}")

