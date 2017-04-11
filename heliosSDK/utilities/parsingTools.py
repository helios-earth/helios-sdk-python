'''
Helper functions for parsing paths and URLs.

@author: Michael A. Bayer
'''
import os
import hashlib
from datetime import datetime

#Python 2 to 3 fix.
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse


def parseTime(data):
    """Parses the time from a URL or image name.
    
    Args:
        data (str): Image URL or name.
    Returns:
        datetime: The parsed time as a datetime object.
    """
    time_string = os.path.splitext(os.path.split(data)[-1])[0].split('_')[-1]
    time_stamp = datetime.strptime(time_string, '%Y%m%d%H%M%S%f')
    return time_stamp

def parseCamera(data):
    """Parses the camera name from a URL or image name.
    
    Args:
        data (str): Image URL or name.
    Returns:
        str: Camera name.
    """
    split1_rev = os.path.splitext(os.path.split(data)[-1])[0][::-1]
    split2 = split1_rev[split1_rev.index('_')+1:][::-1]
    md5_str = hashlib.md5(split2[split2.index('-')+1:].encode('utf-8')).hexdigest()
    
    if split2[0:4] == md5_str[0:4]:
        return split2[5:]
    else:
        return split2
    
def parseImageName(url):
    """Parses the image name from a URL.
    
    Args:
        url (str): Image URL.
    Returns:
        str: Image name.
    """ 
    return os.path.split(url)[-1]

def parseUrl(url):
    """Parses a URL into its components.
    
    Args:
        url (str): Image URL.
    Returns:
        obj: Parsed URL.
    """
    return urlparse(url)