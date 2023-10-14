import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.append(_RePolyA)

from repolya._const import WORKSPACE_AUTOGEN
from repolya.autogen.workflow import do_simple_code
from repolya.autogen.util import cost_usage
from autogen import ChatCompletion


ChatCompletion.start_logging(reset_counter=True, compact=False)


_workspace = './code'
_options = str(WORKSPACE_AUTOGEN / 'service_options')
_recommend = './code/recommend2.py'

if os.path.exists(_recommend):
    _recommend_txt = open(_recommend, 'r').read()
    _task2 = f'''
path of 'service_options': {_options}
'recommend2.py':
{_recommend_txt}
Create the 't-recommend2.py' in which write the test code for get_service_price function of 'recommend2.py' using 'unittest' module. The code you write should be comprehensive and robust to ensure codes will work as expected without bugs, while also conforming to coding standards like PEP8, and being modular, easy to read, and maintainable.

Important Notes:
1. test code should start with following:
"""
import sys
sys.path.append('{_workspace}')
from recommend2 import get_service_price, cheapest_option
import unittest
"""; 
2. test case1 for 'get_service_price': given 'windows-basic-b3-payg', output should be ('windows-basic-b1-payg', 0.075);
3. test case2 for 'get_service_price': given 'linux-standard-s3-payg', output should be ()'linux-standard-s1-payg', 0.095);
4. test case3 for 'get_service_price': given 'nonexistent-service', output should be (None, None);

Remeber, save the test code 't-recommend2.py' to disk.
'''
    re = do_simple_code(_task2)
    print(f"out: '{re}'")
    print(f"cost_usage: {cost_usage(ChatCompletion.logged_history)}")

