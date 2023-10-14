import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.append(_RePolyA)

from repolya.autogen.workflow import do_rd


_task='''查找UDP-GlcA的大规模生成的方法，以及用到的量产菌株'''
re = do_rd(_task)
print(f"out: '{re}'")

