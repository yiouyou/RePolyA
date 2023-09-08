from repolya.paper._paper_scraper import search_papers

from repolya._const import PAPER_PDF
from repolya._log import logger_paper


def querypapers(_query, _limit):
    logger_paper.debug(f"query: '{_query}'")
    # print(_query, _limit)
    papers = []
    try:
        papers = search_papers(_query, limit=_limit, pdir=PAPER_PDF, logger=logger_paper)
        logger_paper.debug(f"papers: {papers}")
    except Exception as e:
        # print(e)
        logger_paper.exception(e)
    return papers

