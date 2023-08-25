#!/usr/bin/env python
# -*- coding: utf-8 -*-
##### paperscraper
from paperscraper.load_dumps import QUERY_FN_DICT
from paperscraper.get_dumps import biorxiv, medrxiv, chemrxiv


# print(QUERY_FN_DICT.keys())
##### ['arxiv', 'pubmed', 'biorxiv', 'chemrxiv', 'medrxiv']
def dump2xiv():
    medrxiv()  #  Takes ~30min and should result in ~35 MB file
    biorxiv()  # Takes ~1h and should result in ~350 MB file
    chemrxiv()  #  Takes ~45min and should result in ~20 MB file

def query2jsonl(_query):
    _q = sum(_query, [])
    _qn = "_".join(_q)
    for i in QUERY_FN_DICT.keys():
        i_file = f"{i}_{_qn}.jsonl"
        i_file = JSONL_ROOT / i_file
        QUERY_FN_DICT[i](_query, output_filepath=i_file)


if __name__ == "__main__":
    dump2xiv()
    # from const import JSONL_ROOT
    # covid19 = ['COVID-19', 'SARS-CoV-2']
    # ai = ['Artificial intelligence', 'Deep learning', 'Machine learning']
    # mi = ['Medical imaging']
    # _query = [covid19, ai, mi]
    # query2jsonl(_query)
else:
    from .const import JSONL_ROOT

