import sys
from loguru import logger
from repolya._const import LOG_ROOT


logger.remove()

_format = "<green>[{extra[job]}]</green> <blue>{level}</blue> <green>{time:YYYY-MM-DD HH:mm:ss}</green> <yellow>{message}</yellow>"
logger.add(sys.stdout, level="INFO", format=_format, colorize=True)

logger.add(LOG_ROOT / "paper.log", level='DEBUG', format=_format, filter=lambda x: x["extra"]["job"] == "paper", backtrace=True, diagnose=True)
logger.add(LOG_ROOT / "writer.log", level='DEBUG', format=_format, filter=lambda x: x["extra"]["job"] == "writer", backtrace=True, diagnose=True)
logger.add(LOG_ROOT / "metagpt.log", level='DEBUG', format=_format, filter=lambda x: x["extra"]["job"] == "metagpt", backtrace=True, diagnose=True)

logger_paper = logger.bind(job="paper")
logger_writer = logger.bind(job="writer")
logger_metagpt = logger.bind(job="metagpt")

