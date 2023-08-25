#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .const import PDF_ROOT
from doi2pdf import doi2pdf
from scidownl import scihub_download

def doi2paper(_doi, _out):
    try:
        _out = PDF_ROOT / _out
        doi2pdf(doi=_doi, output=_out)
        return True
    except Exception as e:
        print(e)
        return False

def title2paper(_name, _out):
    try:
        _out = PDF_ROOT / _out
        doi2pdf(name=_name, output=_out)
        return True
    except Exception as e:
        print(e)
        return False

def url2paper(_url, _out):
    try:
        _out = PDF_ROOT / _out
        doi2pdf(url=_url, output=_out)
        return True
    except Exception as e:
        print(e)
        return False

def pmid2paper(_pmid, _out):
    try:
        _out = PDF_ROOT / _out
        scihub_download(_pmid, paper_type='pmid', out=_out)
        return True
    except Exception as e:
        print(e)
        return False


if __name__ == "__main__":
    doi2paper('10.48550/arXiv.2203.15556', "out4.pdf")
    title2paper('Attention is all you need', 'out1.pdf')
    url2paper("https://arxiv.org/abs/1706.03762", 'out2.pdf')
    pmid2paper('31395057', 'out4.pdf')

