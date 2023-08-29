from doi2pdf import doi2pdf
from scidownl import scihub_download
from repolya._const import PDF_ROOT
from repolya._log import logger_paper


def doi2paper(_doi, _out):
    try:
        _out = PDF_ROOT / _out
        doi2pdf(doi=_doi, output=_out)
        return True
    except Exception as e:
        # print(e)
        logger_paper.exception(e)
        return False


def title2paper(_name, _out):
    try:
        _out = PDF_ROOT / _out
        doi2pdf(name=_name, output=_out)
        return True
    except Exception as e:
        # print(e)
        logger_paper.exception(e)
        return False


def url2paper(_url, _out):
    try:
        _out = PDF_ROOT / _out
        doi2pdf(url=_url, output=_out)
        return True
    except Exception as e:
        # print(e)
        logger_paper.exception(e)
        return False


def pmid2paper(_pmid, _out):
    try:
        _out = PDF_ROOT / _out
        scihub_download(_pmid, paper_type='pmid', out=_out)
        return True
    except Exception as e:
        # print(e)
        logger_paper.exception(e)
        return False
