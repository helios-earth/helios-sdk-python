"""Request manager for all the various components of the Helios SDK."""
import logging

import requests


class RequestManager(object):
    """Manages all API requests."""
    max_retries = 3
    timeout = 5
    ssl_verify = True

    def __init__(self, auth_token, pool_maxsize=32):
        self._auth_token = auth_token

        # Initialize logger
        self._logger = logging.getLogger(__name__)

        # Create API session with authentication credentials
        self.api_session = requests.Session()
        self.api_session.headers.update(
            {self._auth_token['name']: self._auth_token['value']})
        self.api_session.verify = self.ssl_verify
        self.api_session.mount('https://', requests.adapters.HTTPAdapter(
            pool_maxsize=pool_maxsize, max_retries=self.max_retries))

        # Create bare session without credentials
        self.session = requests.Session()
        self.session.verify = self.ssl_verify
        self.session.mount('https://', requests.adapters.HTTPAdapter(
            pool_maxsize=pool_maxsize, max_retries=self.max_retries))

    @property
    def auth_token(self):
        """Access to authentication token."""
        return self._auth_token

    @auth_token.setter
    def auth_token(self, value):
        raise AttributeError('Access to auth_token is restricted.')

    def __del__(self):
        self.api_session.close()
        self.session.close()

    def __request(self, query, use_api_cred=True, request_type='get',
                  **kwargs):

        query = query.replace(' ', '+')
        kwargs['timeout'] = kwargs.get('timeout', self.timeout)

        # Alias the required session
        if use_api_cred:
            sess_alias = self.api_session
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

        # Log and raise exceptions.
        except requests.exceptions.HTTPError:
            self._logger.exception('HTTPError')
            raise
        except requests.exceptions.ConnectionError:
            self._logger.exception('ConnectionError')
            raise
        except requests.exceptions.Timeout:
            self._logger.exception('Timeout')
            raise
        except requests.exceptions.RequestException:
            self._logger.exception('RequestException')
            raise

        return resp

    def get(self, query, use_api_cred=True, **kwargs):
        """
        Perform get request.

        Args:
            query (str): URL string for query.
            use_api_cred (bool, optional): Flag to use API credentials for
                query. Defaults to True.
            **kwargs: Any additional keyword argument for requests.

        Returns:
            Request response.

        """
        return self.__request(query,
                              use_api_cred=use_api_cred,
                              request_type='get',
                              **kwargs)

    def post(self, query, use_api_cred=True, **kwargs):
        """
        Perform post request.

        Args:
            query (str): URL string for query.
            use_api_cred (bool, optional): Flag to use API credentials for
                query. Defaults to True.
            **kwargs: Any additional keyword argument for requests.

        Returns:
            Request response.

        """
        return self.__request(query,
                              use_api_cred=use_api_cred,
                              request_type='post',
                              **kwargs)

    def head(self, query, use_api_cred=True, **kwargs):
        """
        Perform head request.

        Args:
            query (str): URL string for query.
            use_api_cred (bool, optional): Flag to use API credentials for
                query. Defaults to True.
            **kwargs: Any additional keyword argument for requests.

        Returns:
            Request response.

        """
        return self.__request(query,
                              use_api_cred=use_api_cred,
                              request_type='head',
                              **kwargs)

    def delete(self, query, use_api_cred=True, **kwargs):
        """
        Perform delete request.

        Args:
            query (str): URL string for query.
            use_api_cred (bool, optional): Flag to use API credentials for
                query. Defaults to True.
            **kwargs: Any additional keyword argument for requests.

        Returns:
            Request response.

        """
        return self.__request(query,
                              use_api_cred=use_api_cred,
                              request_type='delete',
                              **kwargs)

    def patch(self, query, use_api_cred=True, **kwargs):
        """
        Perform patch request.

        Args:
            query (str): URL string for query.
            use_api_cred (bool, optional): Flag to use API credentials for
                query. Defaults to True.
            **kwargs: Any additional keyword argument for requests.

        Returns:
            Request response.

        """
        return self.__request(query,
                              use_api_cred=use_api_cred,
                              request_type='patch',
                              **kwargs)
