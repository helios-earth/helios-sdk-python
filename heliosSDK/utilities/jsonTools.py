'''
Helper functions for JSON objects.

@author: Michael A. Bayer
'''
import json


def readJsonFile(json_file, **kwargs):
    """Read a json file.
    
    Args:
        json_file (str): Full path to JSON file.
        **kwargs: Any keyword argument from the json.load method.
    Returns:
        dict: JSON formatted dictionary.
    """
    with open(json_file, 'r') as f:
        return json.load(f, **kwargs)

def readJsonString(json_string, **kwargs):
    """Convert a JSON formatted string to JSON.
    
    Args:
        json_string (str): JSON formatted string.
        **kwargs: Any keyword argument from the json.loads method.
    Returns:
        dict: JSON formatted dictionary.
    """
    return json.loads(json_string, **kwargs)

def writeJson(json_dict, f_path, **kwargs):
    """Writes JSON dictionary to file.
    
    Args:
        json_dict (dict): JSON formatted dictionary.
        **kwargs: Any keyword argument from the json.dump method.
    Returns:
        None
    """    
    with open(f_path, 'w+') as f:
        json.dump(json_dict, f, **kwargs)
        
def mergeJson(data, keys):
    """Merge JSON fields into a single list.  Keys can either be a single
    string or a list of strings signifying a chain of "keys" into the 
    dictionary.
    
    Args:
        data (dict): Dictionary to merge data from.
        keys (list): List of keys.  signifying a chain of keys into the dictionary
    Returns:
        list: Merged values.
    """ 
    if not isinstance(keys, list):
        keys = [keys]
    for k in keys:
        data = _mergeDigger(data, k)
    return data

def _mergeDigger(data, key):
    merged_list = []
    for json_slice in data:
        temp = json_slice[key]
        if not isinstance(temp, list):
            temp = [temp]
        merged_list.extend(temp)
    return merged_list
