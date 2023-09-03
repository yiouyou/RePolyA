"""Dump chemRxiv data in JSONL format."""
import os
import sys
from datetime import datetime
from typing import Optional

import pkg_resources

from repolya.paper._paperscraper.get_dumps.utils.chemrxiv import ChemrxivAPI, download_full, parse_dump

from repolya._const import SERVER_DUMP_ROOT
from repolya._log import logger_paper


today = datetime.today().strftime("%Y-%m-%d")
save_folder = SERVER_DUMP_ROOT
save_path = os.path.join(save_folder, f"chemrxiv_{today}.jsonl")


def chemrxiv(
    begin_date: Optional[str] = None,
    end_date: Optional[str] = None,
    save_path: str = save_path,
) -> None:
    """Fetches papers from bichemrxiv based on time range, i.e., begin_date and end_date.
    If the begin_date and end_date are not provided, papers will be fetched from chemrxiv
    from the launch date of chemrxiv until the current date. The fetched papers will be
    stored in jsonl format in save_path.

    Args:
        begin_date (Optional[str], optional): begin date expressed as YYYY-MM-DD.
            Defaults to None.
        end_date (Optional[str], optional): end date expressed as YYYY-MM-DD.
            Defaults to None.
        save_path (str, optional): Path where the dump is stored.
            Defaults to save_path.
    """

    # create API client
    api = ChemrxivAPI(begin_date, end_date)
    # Download the data
    download_full(save_folder, api)
    # Convert to JSONL format.
    parse_dump(save_folder, save_path)
