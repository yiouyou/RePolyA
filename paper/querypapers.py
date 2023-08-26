#!/usr/bin/env python
# -*- coding: utf-8 -*-
##### _paper_scraper
from ._paper_scraper import search_papers

def querypapers(_query, _limit):
    # print(_query, _limit)
    papers = []
    try:
        papers = search_papers(_query, limit=_limit, pdir=PDF_ROOT)
    except Exception as e:
        print(e)
    return papers


if __name__ == "__main__":
    from const import PDF_ROOT
    # _query = 'bayesian model selection'
    _query = 'bispecific antibody manufacture'
    papers = search_papers(_query, limit=10, pdir='./_pdf')
    for i in sorted(papers.keys()):
        print('-'*40)
        print(i)
        print('-'*40)
        for j in sorted(papers[i].keys()):
            print(f"{j}: {papers[i][j]}")
        print("\n")
else:
    from .const import PDF_ROOT

