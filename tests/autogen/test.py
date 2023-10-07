import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.append(_RePolyA)

from repolya.autogen.workflow import do_simple_task, do_simple_code, do_research, do_math, do_plan_task


_do = int(sys.argv[1])

if _do == 1:
    re = do_simple_task("查找一下长沙的天气.")
    print(f"{re}")

if _do == 2:
    re = do_simple_code("For certain cloud services (such as computing), assuming there are several given attributes (such as vCore, memory, iops, storage, backup, etc.) of each computing resource sku, write a flexible and basic recommendation class to filter out unfitted skus and find the lowest price as the recommendation for customers.")
    print(f"{re}")

if _do == 3:
    re = do_research("UDP-GlcA大规模生成")
    print(f"{re}")


if _do == 4:
    re = do_math("Find all numbers $a$ for which the graph of $y=x^2+a$ and the graph of $y=ax$ intersect. Express your answer in interval notation.")
    print(f"{re}")


if _do == 5:
    re = do_plan_task("Suggest a fix to an open good first issue of flaml")
    print(f"{re}")

