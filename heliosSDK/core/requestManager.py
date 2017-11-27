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

    def __request(self, query, use_api_cred=True, request_type='get', **kwargs):
        query = query.replace(' ', '+')
        kwargs['timeout'] = kwargs.get('timeout', self.TIMEOUT)

        # Alias the required session
        if use_api_cred:
            sess_alias = self.apiSession
        else:
            sess_alias = self.session

        # Perform query and raise exceptions
        try:
            if request_type == 'get':
                resp = sess_alias.get(query, **kwargs)
            elif request_type == 'post':
                resp = sess_alias.post(query, **kwargs)
            elif request_type == 'head':
                resp = sess_alias.head(query, **kwargs)
            elif request_type == 'delete':
                resp = sess_alias.delete(query, **kwargs)
            elif request_type == 'patch':
                resp = sess_alias.patch(query, **kwargs)
            else:
                raise ValueError('Unsupported query of type: {}'.format(request_type))
            resp.raise_for_status()
        # Log exceptions and return
        except requests.exceptions.HTTPError:
            self.logger.error('HTTPError {}: {}'.format(resp.status_code, query))
            raise
        except Exception as e:
            self.logger.error('Error: {}'.format(str(e)))
            raise

        return resp

    def get(self, query, use_api_cred=True, **kwargs):
        return self.__request(query,
                              use_api_cred=use_api_cred,
                              request_type='get',
                              **kwargs)

    def post(self, query, use_api_cred=True, **kwargs):
        return self.__request(query,
                              use_api_cred=use_api_cred,
                              request_type='post',
                              **kwargs)

    def head(self, query, use_api_cred=True, **kwargs):
        return self.__request(query,
                              use_api_cred=use_api_cred,
                              request_type='head',
                              **kwargs)

    def delete(self, query, use_api_cred=True, **kwargs):
        return self.__request(query,
                              use_api_cred=use_api_cred,
                              request_type='delete',
                              **kwargs)

    def patch(self, query, use_api_cred=True, **kwargs):
        return self.__request(query,
                              use_api_cred=use_api_cred,
                              request_type='patch',
                              **kwargs)
