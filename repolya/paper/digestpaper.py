from repolya._const import PAPER_PDF
from repolya.paper._digest.pdf import (
    get_imgs_from_pdf,
    get_text_from_pdf,
    pdf_to_faiss,
    multi_query_pdf,
    summarize_pdf_text,
)
from repolya.paper._digest.trans import trans_to

import asyncio


def digest_pdf(_fp):
    get_imgs_from_pdf(_fp)
    get_text_from_pdf(_fp)
    pdf_to_faiss(_fp)

def qa_pdf(_fp, _query, _chain_type):
    _if_lotr = False
    ### qa_faiss_OpenAI_multi_query, not sentence-transformers (lotr)
    return multi_query_pdf(_fp, _query, _chain_type, _if_lotr)
    

def sum_pdf(_fp, _chain_type):
    return summarize_pdf_text(_fp, _chain_type)


def contains_chinese(_str):
    for c in _str:
        if '\u4e00' <= c <= '\u9fff':
            return True
    return False

def trans_en2zh(_en):
    _zh = asyncio.run(trans_to(_en, 'chinese'))
    return _zh

