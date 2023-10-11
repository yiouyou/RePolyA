import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.append(_RePolyA)

from repolya._const import AUTOGEN_REF, WORKSPACE_AUTOGEN
from repolya.autogen.workflow import do_simple_task, do_simple_code, do_simple_code_qa, do_rd, do_math, do_plan_task, do_res, do_rag_doc, do_rag_code

_d = '''linux-standard-s2-payg, 0.19
linux-standard-s3-payg, 0.38
windows-basic-b2-payg, 0.15
windows-basic-b3-payg, 0.3
windows-free-f1-payg, 0
'''
_format = 'os-tier-type-unit'

_workspace = str(WORKSPACE_AUTOGEN)
_options = str(WORKSPACE_AUTOGEN / 'service_options')

_task = f'''
path of workspace: {_workspace}
path of 'service_options': {_options}
In workspace, create the 'recommend.py' in which write two functions:
- def get_service_price(path_of_service_options:str, given_service:str) -> price:float # get the price of the given service from the 'service_options'
- def cheapest_option(path_of_service_options:str, given_service:str) -> [cheapest_service:str, price:float] # select the cheapest alternative service from the 'service_options'
The service options are listed in the format of '{_format}' as follows:
{_d}

Important Notes:
1. the 2nd input of function could be any given service option, such as 'linux-standard-s3-payg' or 'windows-basic-b3-payg';
2. linux os cannot be converted to windows os, which means the windows services cannot be the alternative of linux services, and vice versa;
3. the recommended cheapest price MUST be less than the price of the input service, and should NOT be 0.0;
4. if no alternative service is found, return None, None;

Remeber, save the code to disk.
'''

re = do_simple_code_qa(_task)
print(f"out: '{re}'")

