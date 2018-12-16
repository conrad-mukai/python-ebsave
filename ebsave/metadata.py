"""
ebsave.metadata
instance metadata
"""

# system imports
import requests

# project imports
from .log import LOGGER

# constants
_METADATA_URL = 'http://169.254.169.254/latest/meta-data'


def get_region():
    LOGGER.debug("getting region from metadata")
    return _query_metadata('/placement/availability-zone')[:-1]


def get_instance_id():
    LOGGER.debug("getting instance_id from metadata")
    return _query_metadata('/instance-id')


def _query_metadata(path):
    try:
        response = requests.get(_METADATA_URL + path)
    except requests.exceptions.ConnectionError:
        raise RuntimeError("failed to retrieve metadata: the script doesn't "
                           "appear to be running on an AWS instance")
    return response.text
