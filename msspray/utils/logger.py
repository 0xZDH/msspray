import logging
import sys
from colorama import (  # type: ignore
    Fore,
    init,
)


# Init colorama to switch between Windows
# and Linux
if sys.platform == "win32":
    init(convert=True)


# fmt: off
class text_colors:
    """Color codes for colorized terminal output"""

    HEADER  = Fore.MAGENTA
    OKBLUE  = Fore.BLUE
    OKCYAN  = Fore.CYAN
    OKGREEN = Fore.GREEN
    WARNING = Fore.YELLOW
    FAIL    = Fore.RED
    ENDC    = Fore.RESET


class LoggingLevels:
    CRITICAL = f"{text_colors.FAIL}%s{text_colors.ENDC}" % "crit"     # 50
    ERROR    = f"{text_colors.FAIL}%s{text_colors.ENDC}" % "fail"     # 40
    WARNING  = f"{text_colors.WARNING}%s{text_colors.ENDC}" % "warn"  # 30
    INFO     = f"{text_colors.OKBLUE}%s{text_colors.ENDC}" % "info"   # 20
    DEBUG    = f"{text_colors.OKBLUE}%s{text_colors.ENDC}" % "debg"   # 10


def init_logger(debug: bool):
    """Initialize program logging

    :param debug: if debugging is enabled
    """
    if debug:
        logging_level = logging.DEBUG
        logging_format = "[%(asctime)s] %(levelname)-5s | %(filename)17s:%(lineno)-4s | %(message)s"

    else:
        logging_level = logging.INFO
        logging_format = "[%(asctime)s] %(levelname)-5s | %(message)s"

    logging.basicConfig(format=logging_format, level=logging_level)

    # Update log level names with colorized output
    logging.addLevelName(logging.CRITICAL, LoggingLevels.CRITICAL)  # 50
    logging.addLevelName(logging.ERROR,    LoggingLevels.ERROR)     # 40
    logging.addLevelName(logging.WARNING,  LoggingLevels.WARNING)   # 30
    logging.addLevelName(logging.INFO,     LoggingLevels.INFO)      # 20
    logging.addLevelName(logging.DEBUG,    LoggingLevels.DEBUG)     # 10
