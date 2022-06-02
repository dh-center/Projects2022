import logging
import os
import sys
import traceback
from datetime import datetime
from logging.handlers import RotatingFileHandler

from pytz import timezone

MEGABYTE_IN_BYTES = 2 ** 20

log_file_path = 'logs/log.log'

os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

# https://stackoverflow.com/questions/40088496/how-to-use-pythons-rotatingfilehandler
formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(message)s', datefmt='%d/%m/%Y %I:%M:%S %p')
formatter.converter = lambda *args: datetime.now(tz=timezone('Europe/Moscow')).timetuple()

LOGGER = logging.getLogger("Rotating Log")
LOGGER.setLevel(logging.INFO)

# file log
file_handler = RotatingFileHandler(
    filename=log_file_path,
    maxBytes=20 * MEGABYTE_IN_BYTES,
    backupCount=3
)
file_handler.setFormatter(formatter)

# console log
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)

LOGGER.addHandler(file_handler)
LOGGER.addHandler(console_handler)


# If you want to set the logging level from a command-line option such as:
# --log=INFO
def log(messages, *addition):
    LOGGER.info(messages + "\n ".join(addition))


def log_error(messages, *addition):
    LOGGER.error(messages + "\n ".join(addition))


def log_exp(msg: str, exp: Exception):
    tb = "".join(traceback.TracebackException.from_exception(exp).format())
    log_error(f"Exp : {msg} {exp} {tb}")


if __name__ == '__main__':
    log("test")
