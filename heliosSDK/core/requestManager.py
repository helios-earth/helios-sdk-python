'''
Request manager for all the various components of the Helios SDK
@author: Michael A. Bayer
'''
import requests as r


class RequestManager():
    def __init__(self):
        pass
    
    @staticmethod
    def _getRequest(query, **kwargs):
        query = query.replace(' ', '+')
        resp = r.get(query, **kwargs)
        resp.raise_for_status()
        return resp 
    
    @staticmethod
    def _postRequest(query, **kwargs):
        query = query.replace(' ', '+')
        resp = r.post(query, **kwargs)
        resp.raise_for_status()
        return resp
    
    @staticmethod
    def _headRequest(query, **kwargs):
        query = query.replace(' ', '+')
        resp = r.head(query, **kwargs)
        resp.raise_for_status()
        return resp

    @staticmethod
    def _deleteRequest(query, **kwargs):
        query = query.replace(' ', '+')
        resp = r.delete(query, **kwargs)
        resp.raise_for_status()
        return resp