import os
_RePolyA = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys
sys.path.append(_RePolyA)

from repolya._const import PAPER_PDF
from repolya.paper._digest.pdf import get_imgs_from_pdf, get_text_from_pdf, pdf_to_md


_fp = PAPER_PDF / 'Abanades2021ABlooperFA_10.1101_2021.07.26.453747.pdf'

# get_imgs_from_pdf(_fp)
# get_text_from_pdf(_fp)
pdf_to_md(_fp)
