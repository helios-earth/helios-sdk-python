'''
Request manager for all the various components of the Helios SDK
@author: Michael A. Bayer
'''
import requests as r
from retrying import retry


class RequestManager():
    
    MAX_RETRIES = 5
    
    def __init__(self):
        pass
    
    @staticmethod
    @retry(wait_random_min=500,
           wait_random_max=1000,
           stop_max_attempt_number=MAX_RETRIES)
    def _getRequest(query, **kwargs):
        query = query.replace(' ', '+')
        resp = r.get(query, **kwargs)
        resp.raise_for_status()
        return resp 
    
    @staticmethod
    @retry(wait_random_min=500,
           wait_random_max=1000,
           stop_max_attempt_number=MAX_RETRIES)    
    def _postRequest(query, **kwargs):
        query = query.replace(' ', '+')
        resp = r.post(query, **kwargs)
        resp.raise_for_status()
        return resp
    
    @staticmethod
    @retry(wait_random_min=500,
           wait_random_max=1000,
           stop_max_attempt_number=MAX_RETRIES)    
    def _headRequest(query, **kwargs):
        query = query.replace(' ', '+')
        resp = r.head(query, **kwargs)
        resp.raise_for_status()
        return resp

    @staticmethod
    @retry(wait_random_min=500,
           wait_random_max=1000,
           stop_max_attempt_number=MAX_RETRIES)    
    def _deleteRequest(query, **kwargs):
        query = query.replace(' ', '+')
        resp = r.delete(query, **kwargs)
        resp.raise_for_status()
        return resp