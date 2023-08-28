import sys
from loguru import logger
from repolya._const import LOG_ROOT

logger.remove()
_format = "<green>[{extra[folder]}]</green> <blue>{level}</blue> <green>{time:YYYY-MM-DD HH:mm:ss}</green> <blue>{message}</blue>"
logger.add(sys.stdout, level="INFO", format=_format, 
           colorize=True)

_log = {
    "paper": "paper.log",
    "writer": "writer.log",
    "metagpt": "metagpt.log",
}

for i in _log.keys():
    i_log = LOG_ROOT / _log[i]
    logger.add(i_log, level='INFO', format=_format, 
               filter=lambda x: x["extra"].get("folder")==i, 
               backtrace=True, 
               diagnose=True)

logger_paper = logger.bind(folder="paper")
logger_writer = logger.bind(folder="writer")
logger_metagpt = logger.bind(folder="metagpt")

