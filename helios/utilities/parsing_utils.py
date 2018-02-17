"""Helper functions for paths and URLs."""
import hashlib
import os
from datetime import datetime

# Python 2 to 3 fix.
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse


def parse_time(data):
    """
    Parse time from a URL or image name.

    Args:
        data (str): Image URL or name.
    Returns:
        datetime.datetime: The parsed time as a datetime object.

    """
    time_string = str(os.path.splitext(os.path.split(data)[-1])[0].split('_')[-1])
    time_stamp = datetime.strptime(time_string, '%Y%m%d%H%M%S%f')
    return time_stamp


def parse_camera(data):
    """
    Parse camera name from a URL or image name.

    Args:
        data (str): Image URL or name.
    Returns:
        str: Camera name.

    """

    # Extract tail and remove the extension.
    _, tail = os.path.split(os.path.splitext(data)[0])

    # Split by underscore and remove final index (time string).
    name = '_'.join(tail.split('_')[0:-1])

    # Check for md5 hash (first 4 characters)
    try:
        hash_index = name.index('-')
    except ValueError:
        return name

    # Verify that the first 4 characters are actually the hash.
    md5_hash = hashlib.md5(name[hash_index + 1:].encode('utf-8')).hexdigest()
    if name[0:4] == md5_hash[0:4]:
        return name[5:]
    return name


def parse_image_name(url):
    """
    Parse image name from a URL.

    Args:
        url (str): Image URL.
    Returns:
        str: Image name.

    """
    return os.path.split(url)[-1]


def parse_url(url):
    """
    Parse a URL into its components.

    Args:
        url (str): Image URL.
    Returns:
        urllib.parse.ParseResult: Parsed URL.

    """
    return urlparse(url)
