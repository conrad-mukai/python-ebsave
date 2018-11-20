"""
backup_ebs.log
Module defining logging.
"""

# system imports
import logging

# project imports
from .constants import PROGRAM_NAME

# internal constants
_LOG_LEVELS = (logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR,
               logging.CRITICAL)
_LOGGING_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"

# exported constants
LOG_LEVELS = [logging.getLevelName(l) for l in _LOG_LEVELS]
DEFAULT_LOG_LEVEL = logging.getLevelName(logging.INFO)

# global variables
LOGGER = logging.getLogger(PROGRAM_NAME)

# make some modules quieter
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)


def setup_logging(logfile, loglevel):
    kwargs = {'format': _LOGGING_FORMAT, 'level': loglevel}
    if logfile is not None:
        kwargs['filename'] = logfile
    logging.basicConfig(**kwargs)
