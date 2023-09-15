import re, os, json
import requests
from markdownify import markdownify


def weblink_to_md(_link):
    print(_link)
    _r = requests.get(_link)
    _t1 = markdownify(_r.text, heading_style="ATX")
    _t2 = re.sub(r'\n\s*\n', '\n\n', _t1)
    print(_t2)
    # fn = os.path.join(_dir, f"{str(n).zfill(4)}.md")
    # print(fn)
    # with open(fn, "w") as wf:
    #     wf.write(_t2)

_link = 'https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10238377/'
weblink_to_md(_link)

