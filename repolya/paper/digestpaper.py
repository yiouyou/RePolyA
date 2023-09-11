from repolya._const import PAPER_PDF
from repolya.paper._digest.pdf import (
    get_imgs_from_pdf,
    get_text_from_pdf,
    pdf_to_faiss,
    multi_query_pdf,
    summarize_pdf,
)


def digest_pdf(_fp):
    get_imgs_from_pdf(_fp)
    get_text_from_pdf(_fp)
    pdf_to_faiss(_fp)

def qa_pdf(_fp, _query, _chain_type):
    return multi_query_pdf(_fp, _query, _chain_type, True)
    

def sum_pdf(_fp, _chain_type):
    return summarize_pdf(_fp, _chain_type)
