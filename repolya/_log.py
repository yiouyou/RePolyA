import sys
from loguru import logger
from repolya._const import PROJECT_ROOT

logger.remove()
logger.add(sys.stderr, level="INFO", format="{extra[folder]} {message}")

_log = {
    "writer": "writer.log",
    "metagpt": "metagpt.log",
    "paper": "paper.log",
}

for i in _log:
    i_log = PROJECT_ROOT / 'logs' / _log[i]
    logger.add(i_log, filter=lambda x: x["extra"].get("folder")==i, level='DEBUG', backtrace=True, diagnose=True)

logger_writer = logger.bind(folder="writer")
logger_metagpt = logger.bind(folder="metagpt")
logger_paper = logger.bind(folder="paper")

