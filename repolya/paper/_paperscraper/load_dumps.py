import glob
import os
import sys

import pkg_resources

from repolya.paper._paperscraper.arxiv import get_and_dump_arxiv_papers
from repolya.paper._paperscraper.pubmed import get_and_dump_pubmed_papers
from repolya.paper._paperscraper.xrxiv.xrxiv_query import XRXivQuery

from repolya._const import SERVER_DUMP_ROOT
from repolya._log import logger_paper


# Set up the query dictionary
QUERY_FN_DICT = {
    "arxiv": get_and_dump_arxiv_papers,
    "pubmed": get_and_dump_pubmed_papers,
}
# For biorxiv, chemrxiv and medrxiv search for local dumps
dump_root = SERVER_DUMP_ROOT

for db in ["biorxiv", "chemrxiv", "medrxiv"]:
    dump_paths = glob.glob(os.path.join(dump_root, db + "*"))
    if not dump_paths:
        logger_paper.warning(f" No dump found for {db}. Skipping entry.")
        continue
    elif len(dump_paths) > 1:
        logger_paper.info(f" Multiple dumps found for {db}, taking most recent one")
    path = sorted(dump_paths, reverse=True)[0]

    # Handly empty dumped files (e.g. when API is down)
    if os.path.getsize(path) == 0:
        logger_paper.warning(f"Empty dump for {db}. Skipping entry.")
        continue
    querier = XRXivQuery(path)
    if not querier.errored:
        QUERY_FN_DICT.update({db: querier.search_keywords})
        logger_paper.info(f"Loaded {db} dump with {len(querier.df)} entries")

if len(QUERY_FN_DICT) == 2:
    logger_paper.warning(
        " No dumps found for either biorxiv or medrxiv."
        " Consider using paperscraper.get_dumps.* to fetch the dumps."
    )
