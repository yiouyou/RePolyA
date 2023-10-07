import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.append(_RePolyA)

from repolya.autogen.workflow import do_research, do_simple_ask, do_simple_code


re = do_simple_ask("查找一下长沙的天气.")
print(f"{re}")

# re = do_simple_code("For certain cloud services (such as computing), assuming there are several given attributes (such as vCore, memory, iops, storage, backup, etc.) of each computing resource sku, write a flexible and basic recommendation class to filter out unfitted skus and find the lowest price as the recommendation for customers.")
# print(f"{re}")

# re = do_research("UDP-GlcA大规模生成")
# print(f"{re}")
