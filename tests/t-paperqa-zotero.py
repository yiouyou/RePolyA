import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
sys.path.append(_RePolyA)

from repolya.paper._paperqa.contrib import ZoteroDB
from repolya.paper._paperqa import Docs
from repolya._const import PAPER_PDF

_storage = PAPER_PDF

library_id = os.getenv("ZOTERO_USER_ID")
print(f"zotero ID: {library_id}")

docs = Docs()
zotero = ZoteroDB(
  library_id=library_id,
  library_type="user",
  storage=_storage
)

_z = zotero.iterate(limit=20)
# print(len(_z))

for item in _z:
    # print(f"\n{'-'*40}\n{item.title}\n{item.key}\n{item.num_pages} pages")
    # # print(item.pdf)
    # # print(item.details)
    if item.num_pages > 0 and item.num_pages <= 30:
        print(f"\n{'-'*40}\n{item.title}\n{item.key}\n{item.num_pages} pages")
        docs.add(item.pdf, docname=item.key)

# for item in zotero.iterate(
#         q="large language models",
#         qmode="everything",
#         sort="date",
#         direction="desc",
#         limit=100,
# ):
#     print("Adding", item.title)
#     docs.add(item.pdf, docname=item.key)


while True:
    user_query = input("Please enter your query (type 'exit' to quit): ")
    # 检查是否需要退出
    if user_query.lower() == 'exit':
        print("Exiting the program. Goodbye!")
        break
    # 执行查询并获取答案
    answer = docs.query(user_query)
    # 打印答案
    print(answer)

