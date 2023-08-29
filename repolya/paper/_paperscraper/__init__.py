"""Initialize the module."""
__name__ = "paperscraper"
__version__ = "0.2.7"

import os
import sys
from typing import List, Union

from .load_dumps import QUERY_FN_DICT
from .utils import get_filename_from_query

from repolya._log import logger_paper


def dump_queries(keywords: List[List[Union[str, List[str]]]], dump_root: str) -> None:
    """Performs keyword search on all available servers and dump the results.

    Args:
        keywords (List[List[Union[str, List[str]]]]): List of lists of keywords
            Each second-level list is considered a separate query. Within each
            query, each item (whether str or List[str]) are considered AND
            separated. If an item is again a list, strs are considered synonyms
            (OR separated).
        dump_root (str): Path to root for dumping.
    """

    for idx, keyword in enumerate(keywords):
        for db, f in QUERY_FN_DICT.items():
            logger_paper.info(f" Keyword {idx+1}/{len(keywords)}, DB: {db}")
            filename = get_filename_from_query(keyword)
            os.makedirs(os.path.join(dump_root, db), exist_ok=True)
            f(keyword, output_filepath=os.path.join(dump_root, db, filename))
