import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
sys.path.append(_RePolyA)

from repolya.paper.digestpaper import (
    digest_pdf,
    sum_pdf,
    ans_qlist,
)
from repolya._log import logger_paper
from repolya._const import PAPER_PDF


def find_ext_files(_dir, _ext):
    _files = []
    for root, dirs, files in os.walk(_dir):
        for file in files:
            if file.endswith(_ext):
                full_path = os.path.join(root, file)
                _files.append(full_path)
    return _files


_pdf = find_ext_files(str(PAPER_PDF), '.pdf')
_n = 0
for i in _pdf:
    _n += 1
    print(_n, i)
    _chain_type = "refine"
    digest_pdf(i)
    sum_pdf(i, _chain_type)
    ans_qlist(i)

