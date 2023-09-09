from repolya._const import PAPER_PDF
from repolya.paper._digest.pdf import get_imgs_from_pdf, get_text_from_pdf, pdf_to_faiss


def digest_pdf(_fp):
    get_imgs_from_pdf(_fp)
    get_text_from_pdf(_fp)
    pdf_to_faiss(_fp)

