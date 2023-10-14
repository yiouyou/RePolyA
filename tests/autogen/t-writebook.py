import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.append(_RePolyA)

from repolya.autogen.workflow import do_write_book


_task='''write a book an space exploration for all age groups.'''
re = do_write_book(_task)
print(f"out: '{re}'")

