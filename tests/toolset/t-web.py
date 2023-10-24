import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
sys.path.append(_RePolyA)

from repolya.toolset.load_web import load_urls_to_docs, load_async_chromium_to_docs

url = "https://mp.weixin.qq.com/s?__biz=MzU3MDA0NzE5MA==&mid=2247575773&idx=1&sn=bf11dd65c317c62fcff16b1658bf9f97&chksm=fcf68764cb810e724ef7c178ed3658bf76aa266e607b0beec9de92033a27364af2a6a89215d2&mpshare=1&scene=1&srcid=1024X4wsxDEIlkieIXnlRyc2&sharer_shareinfo=69b20eef2c7b3aac7a951e6f65739058&sharer_shareinfo_first=69b20eef2c7b3aac7a951e6f65739058&exportkey=n_ChQIAhIQZZ%2FMXEBC%2BPF7qsSLBE83xRLvAQIE97dBBAEAAAAAAPfFJU4iHY4AAAAOpnltbLcz9gKNyK89dVj0V6TR5UrNFVpuLr9J6FTng%2BevBlbWsLLQmGsWrzOQ8lyUtA0tB5tGTYMZiiayfGzuqcSnl0BMYOBcq3ETpYB%2BTQPgIg0teRph63DpsT5spv3wMoB%2Fn0yBT4KMvIhzjdZxNsbIhpB%2BOdPBKwRl5FfidhSxNC74wzC5jae7jed7T7%2BBhlcaV2J1FebcAw4G1pILJa6%2BFI%2FaKXKsvRmvQFPkQX7yF1bl9lA2%2FeE7bCdhltCGFDd0drpzS9co8%2BQM8tP%2FZwNN1gG8uFCS&acctmode=0&pass_ticket=p0qTPR7HX9tdweCLPiyJD8O8teoI6nEcf5IVnOPxWVBHWGQLY3lYe%2B%2BMDmQKnoPF&wx_header=0#rd"

_docs = load_urls_to_docs([url])
print(_docs)

# _docs = load_async_chromium_to_docs([url])
# print(_docs)
