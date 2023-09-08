from repolya.paper._paperscraper.load_dumps import QUERY_FN_DICT
from repolya.paper._paperscraper.get_dumps import biorxiv, medrxiv, chemrxiv
from repolya.paper._paperscraper.utils import get_filename_from_query

from repolya._const import PAPER_JSONL
from repolya._log import logger_paper


# print(QUERY_FN_DICT.keys())
##### ['arxiv', 'pubmed', 'biorxiv', 'chemrxiv', 'medrxiv']
@logger_paper.catch
def dump2xiv():
    medrxiv()  #  Takes ~30min and should result in ~35 MB file
    biorxiv()  # Takes ~1h and should result in ~350 MB file
    chemrxiv()  #  Takes ~45min and should result in ~20 MB file


@logger_paper.catch
def query2jsonl(_query):
    _q = sum(_query, [])
    _qn = get_filename_from_query(_query)
    for i in QUERY_FN_DICT.keys():
        i_file = str(PAPER_JSONL / f"{i}_{_qn}")
        # print(i_file)
        logger_paper.debug(i_file)
        QUERY_FN_DICT[i](_query, output_filepath=i_file)

