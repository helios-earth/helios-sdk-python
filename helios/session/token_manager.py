"""Manager for the authorization token required to access the Helios API."""
import json
import os

import requests


class TokenManager(object):
    """Manages API tokens for authentication."""

    token_expiration_threshold = 60  # minutes

    _token_file = os.path.join(os.path.expanduser('~'), '.helios_token')
    _auth_file = os.path.join(os.path.expanduser('~'), '.helios_auth')

    __default_api_url = r'https://api.helios.earth/v1/'

    def __init__(self):
        self.api_url = None
        self.token_url = None
        self.token = None

        self._key_id = None
        self._key_secret = None

        self.get_auth_credentials()

    def start_session(self):
        """
        Begin Helios session.

        Returns:
            tuple: The authentication token and API URL.

        """
        # Check for saved token first. If it doesn't exist then get a token.
        if os.path.exists(self._token_file):
            self.read_token()
            try:
                if not self.verify_token():
                    self.get_token()
            except Exception:
                raise
        else:
            self.get_token()

        return self.token, self.api_url

    def get_token(self):
        """Gets a fresh token and writes the token to file for reuse."""
        try:
            data = {'grant_type': 'client_credentials'}
            auth = (self._key_id, self._key_secret)
            resp = requests.post(self.token_url, data=data, auth=auth,
                                 verify=True)
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            token_url_http = 'http' + self.token_url.split('https')[1]
            data = {'grant_type': 'client_credentials'}
            auth = (self._key_id, self._key_secret)
            resp = requests.post(token_url_http, data=data, auth=auth,
                                 verify=True)

        # If the token cannot be acquired, raise exception.
        resp.raise_for_status()

        token_request = resp.json()
        self.token = {'name': 'Authorization',
                      'value': 'Bearer ' + token_request['access_token']}

        self.write_token()

    def read_token(self):
        """Read token from file."""
        with open(self._token_file, 'r') as token_file:
            self.token = json.load(token_file)

    def write_token(self):
        """Write token to file."""
        with open(self._token_file, 'w+') as token_file:
            json.dump(self.token, token_file)

    def delete_token(self):
        """Delete token file."""
        os.remove(self._token_file)

    def verify_token(self):
        """
        Verifies if the current token is still valid.

        If the token will expire in 60 minutes, then a new token will be
        acquired.

        """
        resp = requests.get(self.api_url + '/session',
                            headers={self.token['name']: self.token['value']},
                            verify=True)
        resp.raise_for_status()

        json_resp = resp.json()

        if json_resp['name'] is None:
            return False
        else:
            expiration_time = json_resp['expires_in'] / 60.0
            if expiration_time < self.token_expiration_threshold:
                self.get_token()
            return True

    def get_auth_credentials(self):
        if 'HELIOS_KEY_ID' in os.environ and 'HELIOS_KEY_SECRET' in os.environ:
            self._key_id = os.environ['HELIOS_KEY_ID']
            self._key_secret = os.environ['HELIOS_KEY_SECRET']

            # Check for API URL override in environment variables
            if 'HELIOS_API_URL' in os.environ:
                self.api_url = os.environ['HELIOS_API_URL']
                self.token_url = os.environ['HELIOS_API_URL'] + '/oauth/token'
            else:
                self.api_url = self.__default_api_url
                self.token_url = self.__default_api_url + '/oauth/token'
        elif os.path.exists(self._auth_file):
            with open(self._auth_file, 'r') as auth_file:
                data = json.load(auth_file)

            self._key_id = data['HELIOS_KEY_ID']
            self._key_secret = data['HELIOS_KEY_SECRET']

            # Check for API URL override in .helios_auth file
            if 'HELIOS_API_URL' in data:
                self.api_url = data['HELIOS_API_URL']
                self.token_url = data['HELIOS_API_URL'] + '/oauth/token'
            else:
                self.api_url = self.__default_api_url
                self.token_url = self.__default_api_url + '/oauth/token'
        else:
            raise Exception('No credentials could be found. Be sure to set '
                            'environment variables or .helios_auth file '
                            'correctly.')
