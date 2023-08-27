from repolya.paper._paper_scraper import search_papers

from repolya._const import PDF_ROOT
from repolya._log import logger_paper


def querypapers(_query, _limit):
    # print(_query, _limit)
    papers = []
    try:
        papers = search_papers(_query, limit=_limit, pdir=PDF_ROOT)
    except Exception as e:
        # print(e)
        logger_paper.exception(e)
    return papers

