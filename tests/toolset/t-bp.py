import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.append(_RePolyA)

from repolya._const import WORKSPACE_RAG
from repolya._log import logger_rag
from repolya.rag.digest_urls import urls_to_faiss_OpenAI
from repolya.rag.vdb_faiss import (
    get_faiss_OpenAI,
    get_faiss_HuggingFace,
)
from repolya.rag.qa_chain import qa_vdb_multi_query

from RePolyA.repolya.toolset._bp import _bp_10_zh, get_inspiration, qlist_to_ans, ans_to_bp, bp_to_md, create_bp_from_urls
from repolya.toolset.tool_stepback import stepback_question, stepback_ddg

import time


pj_urls = [
    "https://mp.weixin.qq.com/s?__biz=MzU3MDA0NzE5MA==&mid=2247575773&idx=1&sn=bf11dd65c317c62fcff16b1658bf9f97&chksm=fcf68764cb810e724ef7c178ed3658bf76aa266e607b0beec9de92033a27364af2a6a89215d2&mpshare=1&scene=1&srcid=1024X4wsxDEIlkieIXnlRyc2&sharer_shareinfo=69b20eef2c7b3aac7a951e6f65739058&sharer_shareinfo_first=69b20eef2c7b3aac7a951e6f65739058&exportkey=n_ChQIAhIQZZ%2FMXEBC%2BPF7qsSLBE83xRLvAQIE97dBBAEAAAAAAPfFJU4iHY4AAAAOpnltbLcz9gKNyK89dVj0V6TR5UrNFVpuLr9J6FTng%2BevBlbWsLLQmGsWrzOQ8lyUtA0tB5tGTYMZiiayfGzuqcSnl0BMYOBcq3ETpYB%2BTQPgIg0teRph63DpsT5spv3wMoB%2Fn0yBT4KMvIhzjdZxNsbIhpB%2BOdPBKwRl5FfidhSxNC74wzC5jae7jed7T7%2BBhlcaV2J1FebcAw4G1pILJa6%2BFI%2FaKXKsvRmvQFPkQX7yF1bl9lA2%2FeE7bCdhltCGFDd0drpzS9co8%2BQM8tP%2FZwNN1gG8uFCS&acctmode=0&pass_ticket=p0qTPR7HX9tdweCLPiyJD8O8teoI6nEcf5IVnOPxWVBHWGQLY3lYe%2B%2BMDmQKnoPF&wx_header=0#rd",
    "https://mp.weixin.qq.com/s?__biz=Mzg4MDcxMzc2OA==&mid=2247486441&idx=1&sn=1807bec943fda134fb53e5fb5c65dfd8&chksm=cf7042aef807cbb8165942877443505bc5e9201949c20ae44475aefe4e2d8327042174cf3d75&mpshare=1&scene=1&srcid=1024FRqoBYYeC8IDIHG6X2fg&sharer_shareinfo=e6c94eeb7960d683070da58eaf176240&sharer_shareinfo_first=e6c94eeb7960d683070da58eaf176240&exportkey=n_ChQIAhIQ%2B6sdOOk8a%2F4jD1XRnCw7WhLvAQIE97dBBAEAAAAAACi3LGQRfscAAAAOpnltbLcz9gKNyK89dVj0Dv4TyMNdRP6CwbpMVy76l007SmPbpLjRwGbCp1ZWf%2FRnVrrfurH1PqD6ycT7JkOB%2Ff3euY1IIrgMR7IhP7h6vBDzzQb1NETCySXky4Zlj7sHDVAPid3t2SkFYN8sa9zVSpD%2BzpQAkJmqUebYSeXkoYJEWg5crQYGCcmD6S3QTFAyuo4uIMI4HIhhoFXKiYZKzDRkjORGvi3O3AWQeAAiUhlJpF%2BY7fW7tyOd8DKLeGDlHalFCGnXLmJ7B4UnHvWzv0lcNPO5Dg1A&acctmode=0&pass_ticket=PnkozxRtY99flZH2qculJbxTG9yqYliflFLLOa6sHytwAgs6dyAF3jm4BlufRWr9&wx_header=0#rd",
    "https://mp.weixin.qq.com/s?__biz=MjM5NzAwMDA4MQ==&mid=2653495194&idx=1&sn=182e8b857c24a0910afaf0ba01409503&chksm=bd3d19648a4a90726cfad558d1d24bb38cf0e851467e69553c818181a451f24896d4015bfe59&mpshare=1&scene=1&srcid=1024erpUXwyfIdKeTyrbdRbw&sharer_shareinfo=cb5cdef097866ae7876d9b10d84ff419&sharer_shareinfo_first=cb5cdef097866ae7876d9b10d84ff419&exportkey=n_ChQIAhIQ0M%2F3CqEqu45xXm9x72uljRLvAQIE97dBBAEAAAAAAEcpKdKGRvcAAAAOpnltbLcz9gKNyK89dVj0nwDz0jtaq6E1YzDE09bK9UUyiyPaR8yNcVAaY6948OawLDGo1EOMiF0xozXgOsL5qWNPamt1qPS%2FyPCVCokm%2BAqUN%2F4Sz2wrFjcxuhVjS9dOPor7qeZKbQqG3HD8Jo5D9KTv5yWVRsO63TiyUPq91C92uq3QU3wxKNqhfwv3fvQ%2FjoIRJvaD5%2BEhGq63bmmx7%2BELZdHxY6mlDuD3xmuQAgoIZ%2B4ETKdXvqNAwBJkhokhKRUKApFJ54Ov5Vew3a6v75pvw%2FC0stJT&acctmode=0&pass_ticket=dhhdANEH4%2FkMdQrizDYriBafgDd2Ondlc9Dh6jPY2q8gFcIK0hzCIsNgiUDKZ%2FrA&wx_header=0#rd",
]

bp_schema_urls = [
    "https://mp.weixin.qq.com/s?__biz=MzAwODE5NDg3NQ==&mid=2651241894&idx=1&sn=cef55d78e8358fcb112161909deedf9b&chksm=808083f2b7f70ae44fb787bd7a3f989d0bde44f8dca2c9084dbebc56b81dceaffd3d83a40e13&mpshare=1&scene=1&srcid=0712rUvBd2qwR1f8J4NiuRVn&sharer_sharetime=1689138875790&sharer_shareid=e232e219e77fde9c69a9fd7891294beb&exportkey=n_ChQIAhIQushYMwnOzvA2rZJC9eMObBLfAQIE97dBBAEAAAAAAChQIh67qFgAAAAOpnltbLcz9gKNyK89dVj0OVwZPhDTnMcgj8QsTg3Awd7xv1V4QZqD0C%2BkRFtFYa4QjhWuMAawvFLparvqWKEbla2GyZOByt8f6UJsMuZnul1mwzfFSN3YvsZh%2FKlH7YB5JXxQOCrg9iQGDylEs8x83lgwVYCe7MI8fUpCRk%2FUKj6LxaMCTMx0VTtp6cFdCOG1ch7eoZXD3dwfhkGN5j0nmV6YEu4zVcRMNdkVa%2BSETpi9SKDNsZOgVsN4cbNaLrj0hoYRcO%2BBNz8%3D&acctmode=0&pass_ticket=QlGoQ3abrBrScGv3K%2BtjIY49pxaeULaYhlaoWtKwSF5kgB%2FXO10zgrGdnHnOZvNC&wx_header=0#rd",
    "https://mp.weixin.qq.com/s?__biz=MzkzOTE3Mjc0Mw==&mid=2247485653&idx=2&sn=2ba3ae266d59928d623790676cb330f0&chksm=c2f5be3df582372b3542d778a132e9c6a8e4a16dff72f29e4cab7d56481d763bfac81ff72ad7&mpshare=1&scene=1&srcid=10249EmVRr2OIkTCcCwymiGg&sharer_shareinfo=ff48ad6cce39dbd48f12ca020f2ca665&sharer_shareinfo_first=ff48ad6cce39dbd48f12ca020f2ca665&exportkey=n_ChQIAhIQWm18TtzqQgmxzKUXfFqhohLfAQIE97dBBAEAAAAAAHSDLkEz4TwAAAAOpnltbLcz9gKNyK89dVj0JQQqNWWeXN2%2FDEspQcDqe8yV7ZjdvW3eCyKHrbFwqg%2F1AXbZVlVxTnW5MIQrt%2BGXpcSOMZee65RV85WDt0oPe%2BUfqlpYPcEoF1sjLNYR%2F9OGesIimFnmEX6G4wB0UNJ0NXoLu8plFCgGRQzaFlUjSYgpOKkHVdcaFQLw%2BWZZmqO1hr1DDv%2BmQ0TZg0KJbZ8JXAg7sbahTSmiHIGaBVszNyxk4CNoFGpnRl2Whinwzo5jGT7r%2BLz1JfQ%3D&acctmode=0&pass_ticket=UCWH4gnvTTUTRtR9fTTdP0SCRnVWTPM%2B50MhWwlo4SGvEFOnHo8GHxVfDmOgzhYk&wx_header=0#rd",
    "https://mp.weixin.qq.com/s?__biz=MzIzMDI2ODQyNQ==&mid=2247491537&idx=1&sn=dd3024e6f45499e5e449af0150a68980&chksm=e8b754b7dfc0dda1573949a4ca442accc6f947fadeaa63ec83914a285567f7650dfbce8e7014&mpshare=1&scene=1&srcid=1024k726iTRWDL76R19WHyKU&sharer_shareinfo=46ae74af33674252763fb57bf3393f37&sharer_shareinfo_first=46ae74af33674252763fb57bf3393f37&exportkey=n_ChQIAhIQBbLLOErYAqhTTbp%2Bv8oOuxLvAQIE97dBBAEAAAAAANBcLZjh2T8AAAAOpnltbLcz9gKNyK89dVj0LKQB1Q07ORc7PQ3inRPsDr9HXw%2B6LPd9fPeHWNWca7MDl3pCUOKmPO80OtQTq%2BEZpaj5vDG5m%2Fs33PDOgWU4Uw%2Bth0YBJsWz1cMY8iZu%2BzLVDT0oXM8EE455pms2o%2Bltk27tbvSqyOTtHeeMAStbYibdiWydVwjxXxF8zebNHPJuZbb0h9qQCrX7mYftCfEuj1iTIwqGUpR%2B%2BJarLR8%2Bf41Qp51A8FxZnMFc3E%2FKTwKImcakA4mGL3P1p2BwTrqaVNufOHzfAHdI&acctmode=0&pass_ticket=Rcd%2FZr3rGEN5PVPhxCms7S0GGBmjZXfxUvmbzB22Lakg%2BFt7diGeqKzn6KXtl%2Bme&wx_header=0#rd",
]


_dir = str(WORKSPACE_RAG / "cq_bp")
if not os.path.exists(_dir):
    os.makedirs(_dir)
vdb_pj = str(WORKSPACE_RAG / "cq_bp_pj_openai")
vdb_bp = str(WORKSPACE_RAG / "cq_bp_schema_openai")
# urls_to_faiss_OpenAI(pj_urls, vdb_pj, str(WORKSPACE_RAG / "cq_bp_pj_clean_txt"))
# urls_to_faiss_OpenAI(bp_schema_urls, vdb_bp, str(WORKSPACE_RAG / "cq_bp_schema_clean_txt"))
# for _topic in _bp_10_zh.keys():
#     _re, _token_cost = get_inspiration("新式茶饮", _topic)
#     with open(os.path.join(_dir, f"{_topic}.qlist"), "w") as f:
#         f.write(f"{_re}\n\n{_token_cost}")
# qlist_to_ans(_dir, vdb_pj)
# ans_to_bp(_dir, '新式茶饮')
# bp_to_md(_dir, '新式茶饮')


# create_bp_from_urls(pj_urls, '新式茶饮')


##### test
# print(stepback_ddg(sys.argv[1]))
# _ans, _step, _token_cost, _time = qa_faiss_openai(sys.argv[1], vdb_pj)
# print(_ans)
# # print(_step)
# print(_token_cost)
# print(_time)

