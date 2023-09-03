import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
sys.path.append(_RePolyA)

from repolya.paper.download import doi2paper
from repolya.paper.download import title2paper
from repolya.paper.download import url2paper
from repolya.paper.download import pmid2paper


doi2paper('10.48550/arXiv.2203.15556', "out0.pdf")
title2paper('Attention is all you need', 'out1.pdf')
url2paper("https://arxiv.org/abs/1706.03762", 'out2.pdf')
pmid2paper('31395057', 'out3.pdf')

