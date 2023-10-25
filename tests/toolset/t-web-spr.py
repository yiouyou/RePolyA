import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.append(_RePolyA)

from repolya.toolset.load_web import load_urls_to_docs, load_async_chromium_to_docs
from repolya.toolset.tool_spr import spr_generator, spr_unpack, zh_spr_generator, zh_spr_unpack
from pprint import pprint
import re


url = [
    "https://mp.weixin.qq.com/s?__biz=MzU3MDA0NzE5MA==&mid=2247575773&idx=1&sn=bf11dd65c317c62fcff16b1658bf9f97&chksm=fcf68764cb810e724ef7c178ed3658bf76aa266e607b0beec9de92033a27364af2a6a89215d2&mpshare=1&scene=1&srcid=1024X4wsxDEIlkieIXnlRyc2&sharer_shareinfo=69b20eef2c7b3aac7a951e6f65739058&sharer_shareinfo_first=69b20eef2c7b3aac7a951e6f65739058&exportkey=n_ChQIAhIQZZ%2FMXEBC%2BPF7qsSLBE83xRLvAQIE97dBBAEAAAAAAPfFJU4iHY4AAAAOpnltbLcz9gKNyK89dVj0V6TR5UrNFVpuLr9J6FTng%2BevBlbWsLLQmGsWrzOQ8lyUtA0tB5tGTYMZiiayfGzuqcSnl0BMYOBcq3ETpYB%2BTQPgIg0teRph63DpsT5spv3wMoB%2Fn0yBT4KMvIhzjdZxNsbIhpB%2BOdPBKwRl5FfidhSxNC74wzC5jae7jed7T7%2BBhlcaV2J1FebcAw4G1pILJa6%2BFI%2FaKXKsvRmvQFPkQX7yF1bl9lA2%2FeE7bCdhltCGFDd0drpzS9co8%2BQM8tP%2FZwNN1gG8uFCS&acctmode=0&pass_ticket=p0qTPR7HX9tdweCLPiyJD8O8teoI6nEcf5IVnOPxWVBHWGQLY3lYe%2B%2BMDmQKnoPF&wx_header=0#rd",
    "https://mp.weixin.qq.com/s?__biz=Mzg4MDcxMzc2OA==&mid=2247486441&idx=1&sn=1807bec943fda134fb53e5fb5c65dfd8&chksm=cf7042aef807cbb8165942877443505bc5e9201949c20ae44475aefe4e2d8327042174cf3d75&mpshare=1&scene=1&srcid=1024FRqoBYYeC8IDIHG6X2fg&sharer_shareinfo=e6c94eeb7960d683070da58eaf176240&sharer_shareinfo_first=e6c94eeb7960d683070da58eaf176240&exportkey=n_ChQIAhIQ%2B6sdOOk8a%2F4jD1XRnCw7WhLvAQIE97dBBAEAAAAAACi3LGQRfscAAAAOpnltbLcz9gKNyK89dVj0Dv4TyMNdRP6CwbpMVy76l007SmPbpLjRwGbCp1ZWf%2FRnVrrfurH1PqD6ycT7JkOB%2Ff3euY1IIrgMR7IhP7h6vBDzzQb1NETCySXky4Zlj7sHDVAPid3t2SkFYN8sa9zVSpD%2BzpQAkJmqUebYSeXkoYJEWg5crQYGCcmD6S3QTFAyuo4uIMI4HIhhoFXKiYZKzDRkjORGvi3O3AWQeAAiUhlJpF%2BY7fW7tyOd8DKLeGDlHalFCGnXLmJ7B4UnHvWzv0lcNPO5Dg1A&acctmode=0&pass_ticket=PnkozxRtY99flZH2qculJbxTG9yqYliflFLLOa6sHytwAgs6dyAF3jm4BlufRWr9&wx_header=0#rd",
    "https://mp.weixin.qq.com/s?__biz=MjM5NzAwMDA4MQ==&mid=2653495194&idx=1&sn=182e8b857c24a0910afaf0ba01409503&chksm=bd3d19648a4a90726cfad558d1d24bb38cf0e851467e69553c818181a451f24896d4015bfe59&mpshare=1&scene=1&srcid=1024erpUXwyfIdKeTyrbdRbw&sharer_shareinfo=cb5cdef097866ae7876d9b10d84ff419&sharer_shareinfo_first=cb5cdef097866ae7876d9b10d84ff419&exportkey=n_ChQIAhIQ0M%2F3CqEqu45xXm9x72uljRLvAQIE97dBBAEAAAAAAEcpKdKGRvcAAAAOpnltbLcz9gKNyK89dVj0nwDz0jtaq6E1YzDE09bK9UUyiyPaR8yNcVAaY6948OawLDGo1EOMiF0xozXgOsL5qWNPamt1qPS%2FyPCVCokm%2BAqUN%2F4Sz2wrFjcxuhVjS9dOPor7qeZKbQqG3HD8Jo5D9KTv5yWVRsO63TiyUPq91C92uq3QU3wxKNqhfwv3fvQ%2FjoIRJvaD5%2BEhGq63bmmx7%2BELZdHxY6mlDuD3xmuQAgoIZ%2B4ETKdXvqNAwBJkhokhKRUKApFJ54Ov5Vew3a6v75pvw%2FC0stJT&acctmode=0&pass_ticket=dhhdANEH4%2FkMdQrizDYriBafgDd2Ondlc9Dh6jPY2q8gFcIK0hzCIsNgiUDKZ%2FrA&wx_header=0#rd",
]

url = [
    "https://mp.weixin.qq.com/s?__biz=MzAwODE5NDg3NQ==&mid=2651241894&idx=1&sn=cef55d78e8358fcb112161909deedf9b&chksm=808083f2b7f70ae44fb787bd7a3f989d0bde44f8dca2c9084dbebc56b81dceaffd3d83a40e13&mpshare=1&scene=1&srcid=0712rUvBd2qwR1f8J4NiuRVn&sharer_sharetime=1689138875790&sharer_shareid=e232e219e77fde9c69a9fd7891294beb&exportkey=n_ChQIAhIQushYMwnOzvA2rZJC9eMObBLfAQIE97dBBAEAAAAAAChQIh67qFgAAAAOpnltbLcz9gKNyK89dVj0OVwZPhDTnMcgj8QsTg3Awd7xv1V4QZqD0C%2BkRFtFYa4QjhWuMAawvFLparvqWKEbla2GyZOByt8f6UJsMuZnul1mwzfFSN3YvsZh%2FKlH7YB5JXxQOCrg9iQGDylEs8x83lgwVYCe7MI8fUpCRk%2FUKj6LxaMCTMx0VTtp6cFdCOG1ch7eoZXD3dwfhkGN5j0nmV6YEu4zVcRMNdkVa%2BSETpi9SKDNsZOgVsN4cbNaLrj0hoYRcO%2BBNz8%3D&acctmode=0&pass_ticket=QlGoQ3abrBrScGv3K%2BtjIY49pxaeULaYhlaoWtKwSF5kgB%2FXO10zgrGdnHnOZvNC&wx_header=0#rd",
    "https://mp.weixin.qq.com/s?__biz=MzkzOTE3Mjc0Mw==&mid=2247485653&idx=2&sn=2ba3ae266d59928d623790676cb330f0&chksm=c2f5be3df582372b3542d778a132e9c6a8e4a16dff72f29e4cab7d56481d763bfac81ff72ad7&mpshare=1&scene=1&srcid=10249EmVRr2OIkTCcCwymiGg&sharer_shareinfo=ff48ad6cce39dbd48f12ca020f2ca665&sharer_shareinfo_first=ff48ad6cce39dbd48f12ca020f2ca665&exportkey=n_ChQIAhIQWm18TtzqQgmxzKUXfFqhohLfAQIE97dBBAEAAAAAAHSDLkEz4TwAAAAOpnltbLcz9gKNyK89dVj0JQQqNWWeXN2%2FDEspQcDqe8yV7ZjdvW3eCyKHrbFwqg%2F1AXbZVlVxTnW5MIQrt%2BGXpcSOMZee65RV85WDt0oPe%2BUfqlpYPcEoF1sjLNYR%2F9OGesIimFnmEX6G4wB0UNJ0NXoLu8plFCgGRQzaFlUjSYgpOKkHVdcaFQLw%2BWZZmqO1hr1DDv%2BmQ0TZg0KJbZ8JXAg7sbahTSmiHIGaBVszNyxk4CNoFGpnRl2Whinwzo5jGT7r%2BLz1JfQ%3D&acctmode=0&pass_ticket=UCWH4gnvTTUTRtR9fTTdP0SCRnVWTPM%2B50MhWwlo4SGvEFOnHo8GHxVfDmOgzhYk&wx_header=0#rd",
    # "https://mp.weixin.qq.com/s?__biz=MzI5NDc5NDc0NQ==&mid=2247485961&idx=1&sn=61a87309a20ed4b8de45ef9ecf6304ee&chksm=ec5c2e9fdb2ba78904def09b3ebb2cdfbb7178caade9f3f47a0a1a3acd60cc53e4db9e9b660c&mpshare=1&scene=1&srcid=1024nc2YtJcMLne07ZEz8qX0&sharer_shareinfo=3f23e2a44feb2a9cc29f9fc2f9ca9e4f&sharer_shareinfo_first=3f23e2a44feb2a9cc29f9fc2f9ca9e4f&exportkey=n_ChQIAhIQm%2BegsukDc%2BCujrSmsEcg7hLpAQIE97dBBAEAAAAAAN9oCbJhAGAAAAAOpnltbLcz9gKNyK89dVj0qoDqGsU9mK%2Fb%2FoNVLh4jUTwxGCsm%2Fz4vXydyk1y%2B7ka8NpD6Za3Ftwt%2B%2B8828V0LhHLhcQZ28Scyftva8fJul9JjFv1EyvERajg%2BS8MCPsvQV8tt359Ia8RSKUTCxmvNxyybvfoHY3i4KR9DOy0EG6SvYZViVH3U%2BrSWx7mI3ICQkvR6qcMWuwPqMh%2F88itUzoVHQaqTTR3uQPYAal3%2BeHNVtuDiOr3oDnQBQYhLbuSHaG0TkgnZpJuyJ9X6K0OLUmcc&acctmode=0&pass_ticket=eywPv%2B8Snoj9qQeDhLqqAiIvugr8RkNSw4AavxIX8VyKNz16ZJ6D1YsLIEKhHlOI&wx_header=0#rd",
    # "https://mp.weixin.qq.com/s?__biz=MzkzMTIwNzQ2Ng==&mid=2247483885&idx=2&sn=0f8dc5a635ba45437dc50ecd449de9da&chksm=c26fc1a8f51848befedb233d064d85a30635f62e169e44d3c20839a545cbd59cc838b46b3c26&mpshare=1&scene=1&srcid=10241VNHaHZ6e9zaV1F1bGuv&sharer_shareinfo=627fc093b4af5ec69e636e37be7524d0&sharer_shareinfo_first=627fc093b4af5ec69e636e37be7524d0&exportkey=n_ChQIAhIQ1OfVSqtwGMDBbW8fZqtIixLvAQIE97dBBAEAAAAAAIjhOnCseWYAAAAOpnltbLcz9gKNyK89dVj01fHSGyeaa9OLgxcOVZ54pGVu0LqvS%2Bt04QHgCYqTV94BOE%2Baw6ypyX%2FmwOyu5m%2F%2BtTg1enMQUBZRj44%2FBJYhkTU8IFqXiei6sTEanuOIdy3KsjLD6F9b3OYODk1me6jx85H8xkz1MOtYDP56oFyvB8%2FpAU44ev2AMlR9FIJB1SVezUgVj4BQ6DOmNucSzDuj%2Fhs3U31OrXjU1IqeccRr8ETrgpCSxURh9TIR63mna9StvD9C5tpTx94YUJws0rL3CQrLvYlg4Qpb&acctmode=0&pass_ticket=Fr95Z%2FuUtGo%2F1l3A9A5qabKh5hdFmUnFKTy0zB4tiM%2BSQrkifvvPOgjAE5I8jlk2&wx_header=0#rd",
    "https://mp.weixin.qq.com/s?__biz=MzIzMDI2ODQyNQ==&mid=2247491537&idx=1&sn=dd3024e6f45499e5e449af0150a68980&chksm=e8b754b7dfc0dda1573949a4ca442accc6f947fadeaa63ec83914a285567f7650dfbce8e7014&mpshare=1&scene=1&srcid=1024k726iTRWDL76R19WHyKU&sharer_shareinfo=46ae74af33674252763fb57bf3393f37&sharer_shareinfo_first=46ae74af33674252763fb57bf3393f37&exportkey=n_ChQIAhIQBbLLOErYAqhTTbp%2Bv8oOuxLvAQIE97dBBAEAAAAAANBcLZjh2T8AAAAOpnltbLcz9gKNyK89dVj0LKQB1Q07ORc7PQ3inRPsDr9HXw%2B6LPd9fPeHWNWca7MDl3pCUOKmPO80OtQTq%2BEZpaj5vDG5m%2Fs33PDOgWU4Uw%2Bth0YBJsWz1cMY8iZu%2BzLVDT0oXM8EE455pms2o%2Bltk27tbvSqyOTtHeeMAStbYibdiWydVwjxXxF8zebNHPJuZbb0h9qQCrX7mYftCfEuj1iTIwqGUpR%2B%2BJarLR8%2Bf41Qp51A8FxZnMFc3E%2FKTwKImcakA4mGL3P1p2BwTrqaVNufOHzfAHdI&acctmode=0&pass_ticket=Rcd%2FZr3rGEN5PVPhxCms7S0GGBmjZXfxUvmbzB22Lakg%2BFt7diGeqKzn6KXtl%2Bme&wx_header=0#rd",
]

_docs = load_urls_to_docs(url)

def clean_wx_article(text):
    # 替换多个连续换行为一个
    text = re.sub(r'\n+', '\n', text)
    # 替换多个连续空格为一个
    text = re.sub(r' +', ' ', text)
    # 使用正则表达式替换每行开头的空格
    text = re.sub(r'^\s+', '', text, flags=re.MULTILINE)
    text = text.split('预览时标签不可点')
    return text[0]

for i in _docs:
    _d = i.to_json()
    _page_content = _d['kwargs']['page_content']
    # print(_page_content)
    _metadata = _d['kwargs']['metadata']
    i_clean = clean_wx_article(_page_content)
    print(_metadata)
    print(f"{i_clean}")
    # _spr, _token_cost = zh_spr_generator(i_clean)
    # print(_spr)
    # print(_token_cost)


# _tt = """
# - 酒馆鼓励顾客自我服务，自带食物分享，甚至自己打酒。
# - 酒馆每年会有200多场活动，客人可以是活动发起人，活动内容多样，包括音乐会、即兴演讲、论文指导等。
# - 酒馆的商业模式野生打法，反商业常识，难以大规模复制。
# """
# _txt, _token_cost = spr_unpack(_tt)
# print(_txt)
# print(_token_cost)

# _docs = load_async_chromium_to_docs([url])
# print(_docs)


