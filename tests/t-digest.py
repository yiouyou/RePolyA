import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
sys.path.append(_RePolyA)

from repolya._const import PAPER_PDF
from repolya.paper.digestpaper import digest_pdf, qa_pdf


# _fp = PAPER_PDF / 'Abanades2021ABlooperFA_10.1101_2021.07.26.453747.pdf'
_fp = PAPER_PDF / 'The company landscape for artificial intelligence in large-molecule drug discovery.pdf'

digest_pdf(_fp)

qa_pdf(_fp, 'Whats the paper talking about?')
