import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.append(_RePolyA)

from repolya.autogen.workflow import do_simple_task, do_simple_code, do_rd, do_math, do_plan_task, do_res, do_rag_doc, do_rag_code


_do = int(sys.argv[1])

if _do == 1:
    re = do_simple_task("查找一下长沙的天气.")
    print(f"{re}")

if _do == 2:
    re = do_simple_code("For certain cloud services (such as computing), assuming there are several given attributes (such as vCore, memory, iops, storage, backup, etc.) of each computing resource sku, write a flexible and basic recommendation class to filter out unfitted skus and find the lowest price as the recommendation for customers.")
    print(f"{re}")

if _do == 3:
    re = do_rd("UDP-GlcA大规模生成")
    print(f"{re}")


if _do == 4:
    re = do_math("Find all numbers $a$ for which the graph of $y=x^2+a$ and the graph of $y=ax$ intersect. Express your answer in interval notation.")
    print(f"{re}")


if _do == 5:
    re = do_plan_task("Suggest a fix to an open good first issue of flaml")
    print(f"{re}")


if _do == 6:
    re = do_res("find papers on LLM applications from arxiv in the last week, create a markdown table of different domains.")
    print(f"{re}")


if _do == 7:
    re = do_rag_doc("Which film came out first, Blind Shaft or The Mask Of Fu Manchu?")
    print(f"{re}")


if _do == 8:
    re = do_rag_code("How can I use FLAML to perform a classification task and use spark to do parallel training. Train 30 seconds and force cancel jobs if time limit is reached.")
    print(f"{re}")

