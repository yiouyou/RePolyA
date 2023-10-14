import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.append(_RePolyA)

from repolya._const import WORKSPACE_AUTOGEN
from repolya.autogen.workflow import do_simple_code
from repolya.autogen.util import cost_usage
from autogen import ChatCompletion


ChatCompletion.start_logging(reset_counter=True, compact=False)


_d = '''linux-standard-s2-payg, 0.19
linux-standard-s3-payg, 0.38
windows-basic-b2-payg, 0.15
windows-basic-b3-payg, 0.3
windows-free-f1-payg, 0
'''
_format = 'os-tier-type-unit'

_workspace = './code'
_options = str(WORKSPACE_AUTOGEN / 'service_options')

_task1 = f'''
path of 'service_options': {_options}
Create the 'recommend2.py' in which write two functions:
- def get_service_price(path_of_service_options:str, given_service:str) -> price:float # get the price of the given service from the 'service_options'
- def cheapest_option(path_of_service_options:str, given_service:str) -> [cheapest_service:str, price:float] # select the cheapest alternative service from the 'service_options'
The service options are listed in the format of '{_format}' as follows:
{_d}

The code you write should be comprehensive and robust to ensure codes will work as expected without bugs, while also conforming to coding standards like PEP8, and being modular, easy to read, and maintainable.

Important Notes:
1. the 2nd input of function could be any given service option, such as 'linux-standard-s3-payg' or 'windows-basic-b3-payg';
2. linux os cannot be converted to windows os, which means the windows services cannot be the alternative of linux services, and vice versa;
3. the recommended cheapest price MUST be less than the price of the input service, and should NOT be 0.0;
4. if no alternative service is found, return None, None;

Remeber, save the code to disk.
'''

re = do_simple_code(_task1)
print(f"out: '{re}'")
print(f"cost_usage: {cost_usage(ChatCompletion.logged_history)}")

