'''
Request manager for all the various components of the Helios SDK
@author: Michael A. Bayer
'''
import requests
from heliosSDK import AUTH_TOKEN


class RequestManager(object):
    MAX_RETRIES = 5
    SSL_VERIFY = True

    def __init__(self, pool_maxsize=32):
        self.session = requests.Session()
        self.session.headers = {AUTH_TOKEN['name']: AUTH_TOKEN['value']}
        self.session.verify = self.SSL_VERIFY
        self.session.mount('https://', requests.adapters.HTTPAdapter(pool_maxsize=pool_maxsize,
                                                                     max_retries=self.MAX_RETRIES))

    def __del__(self):
        self.session.close()

    def _getRequest(self, query, **kwargs):
        query = query.replace(' ', '+')
        try:
            resp = self.session.get(query, **kwargs)
            resp.raise_for_status()
        finally:
            return resp

    def _postRequest(self, query, **kwargs):
        query = query.replace(' ', '+')
        try:
            resp = self.session.post(query, **kwargs)
            resp.raise_for_status()
        finally:
            return resp

    def _headRequest(self, query, **kwargs):
        query = query.replace(' ', '+')
        try:
            resp = self.session.head(query, **kwargs)
            resp.raise_for_status()
        finally:
            return resp

    def _deleteRequest(self, query, **kwargs):
        query = query.replace(' ', '+')
        try:
            resp = self.session.delete(query, **kwargs)
            resp.raise_for_status()
        finally:
            return resp
