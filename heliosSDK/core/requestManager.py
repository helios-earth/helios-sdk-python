'''
Request manager for all the various components of the Helios SDK
@author: Michael A. Bayer
'''
import logging

import requests

from heliosSDK import AUTH_TOKEN


class RequestManager(object):
    MAX_RETRIES = 3
    TIMEOUT = 5
    SSL_VERIFY = True

    def __init__(self, pool_maxsize=32):
        # Initialize logger
        self.logger = logging.getLogger(__name__)

        # Create API session with authentication credentials
        self.apiSession = requests.Session()
        self.apiSession.headers = {AUTH_TOKEN['name']: AUTH_TOKEN['value']}
        self.apiSession.verify = self.SSL_VERIFY
        self.apiSession.mount('https://', requests.adapters.HTTPAdapter(pool_maxsize=pool_maxsize,
                                                                        max_retries=self.MAX_RETRIES))

        # Create bare session without credentials
        self.session = requests.Session()
        self.session.verify = self.SSL_VERIFY
        self.session.mount('https://', requests.adapters.HTTPAdapter(pool_maxsize=pool_maxsize,
                                                                     max_retries=self.MAX_RETRIES))

    def __del__(self):
        self.apiSession.close()
        self.session.close()

    def get(self, query, use_api_cred=True, **kwargs):
        query = query.replace(' ', '+')
        kwargs['timeout'] = kwargs.get('timeout', self.TIMEOUT)
        try:
            if use_api_cred:
                resp = self.apiSession.get(query, **kwargs)
            else:
                resp = self.session.get(query, **kwargs)
        # If the exception isn't a typical http error code, log the exception and raise
        except Exception as e:
            self.logger.error('ConnectTimeout Error {}: {}'.format(e, query))
            raise e

        return resp

    def post(self, query, use_api_cred=True, **kwargs):
        query = query.replace(' ', '+')
        kwargs['timeout'] = kwargs.get('timeout', self.TIMEOUT)
        try:
            if use_api_cred:
                resp = self.apiSession.post(query, **kwargs)
            else:
                resp = self.session.post(query, **kwargs)
        # If the exception isn't a typical http error code, log the exception and raise
        except Exception as e:
            self.logger.error('ConnectTimeout Error {}: {}'.format(e, query))
            raise e

        return resp

    def head(self, query, use_api_cred=True, **kwargs):
        query = query.replace(' ', '+')
        kwargs['timeout'] = kwargs.get('timeout', self.TIMEOUT)
        try:
            if use_api_cred:
                resp = self.apiSession.head(query, **kwargs)
            else:
                resp = self.session.head(query, **kwargs)
        # If the exception isn't a typical http error code, log the exception and raise
        except Exception as e:
            self.logger.error('ConnectTimeout Error {}: {}'.format(e, query))
            raise e

        return resp

    def delete(self, query, use_api_cred=True, **kwargs):
        query = query.replace(' ', '+')
        kwargs['timeout'] = kwargs.get('timeout', self.TIMEOUT)
        try:
            if use_api_cred:
                resp = self.apiSession.delete(query, **kwargs)
            else:
                resp = self.session.delete(query, **kwargs)
        # If the exception isn't a typical http error code, log the exception and raise
        except Exception as e:
            self.logger.error('ConnectTimeout Error {}: {}'.format(e, query))
            raise e

        return resp
