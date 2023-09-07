import sys
from loguru import logger
from repolya._const import LOG_CHAT, LOG_PAPER, LOG_WRITER, LOG_METAGPT, LOG_CODER


logger.remove()

_format = "<green>[{extra[job]}]</green> <blue>{level}</blue> <green>{time:YYYY-MM-DD HH:mm:ss}</green> <yellow>{message}</yellow>"
logger.add(sys.stdout, level="INFO", format=_format, colorize=True)

logger.add(LOG_CHAT, level='INFO', format=_format, filter=lambda x: x["extra"]["job"] == "chat")
logger.add(LOG_PAPER, level='DEBUG', format=_format, filter=lambda x: x["extra"]["job"] == "paper", backtrace=True, diagnose=True)
logger.add(LOG_WRITER, level='DEBUG', format=_format, filter=lambda x: x["extra"]["job"] == "writer", backtrace=True, diagnose=True)
logger.add(LOG_METAGPT, level='DEBUG', format=_format, filter=lambda x: x["extra"]["job"] == "metagpt", backtrace=True, diagnose=True)
logger.add(LOG_CODER, level='INFO', format=_format, filter=lambda x: x["extra"]["job"] == "coder", backtrace=True, diagnose=True)

logger_chat = logger.bind(job="chat")
logger_paper = logger.bind(job="paper")
logger_writer = logger.bind(job="writer")
logger_metagpt = logger.bind(job="metagpt")
logger_coder = logger.bind(job="coder")

