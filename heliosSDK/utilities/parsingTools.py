'''
Helper functions for parsing paths and URLs.

@author: Michael A. Bayer
'''
import os
import hashlib
from urlparse import urlparse
from datetime import datetime


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
    split1 = os.path.splitext(os.path.split(data)[-1])[0].split('_')[0]
    md5_str = hashlib.md5(split1[split1.index('-')+1:].encode('utf-8')).hexdigest()
    
    if split1[0:4] == md5_str[0:4]:
        return split1[5:]
    else:
        return split1
    
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


if __name__=='__main__':
    x = r'https://helios-u-exelis.s3.amazonaws.com/collections/9d0bf4fa-affb-4d45-81e7-8c9b11ea9119/TL-15939_20150409185836059.jpg'
    print(parseTime(x))