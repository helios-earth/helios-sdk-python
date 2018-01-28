"""Manager for the authorization token required to access the Helios API."""
import json
import os

import requests

# Python 2 compatibility.
try:
    FileNotFoundError
except NameError:
    FileNotFoundError = IOError


class SessionManager(object):
    """Manages API tokens for authentication."""

    token_expiration_threshold = 60  # minutes

    _token_file = os.path.join(os.path.expanduser('~'), '.helios_token')
    _auth_file = os.path.join(os.path.expanduser('~'), '.helios_auth')
    _default_api_url = r'https://api.helios.earth/v1/'

    def __init__(self):
        # The token will be established with a call to the start_session method.
        self.token = None

        # Try to load essential authentication data from environment or file.
        if 'HELIOS_KEY_ID' in os.environ and 'HELIOS_KEY_SECRET' in os.environ:
            data = os.environ
        else:
            try:
                with open(self._auth_file, 'r') as auth_file:
                    data = json.load(auth_file)
            except (IOError, FileNotFoundError):
                raise Exception('No credentials could be found. Be sure to '
                                'set environment variables or setup a '
                                '.helios_auth file.')

        # Extract relevant authentication information from data.
        self._key_id = data['HELIOS_KEY_ID']
        self._key_secret = data['HELIOS_KEY_SECRET']
        try:
            self.api_url = data['HELIOS_API_URL']
        except KeyError:
            self.api_url = self._default_api_url

        self.token_url = self.api_url + '/oauth/token'

    def start_session(self):
        """
        Begin Helios session.

        This will establish a token for the session.

        """
        # Check for saved token first. If it doesn't exist then get a token.
        try:
            self.read_token()
            if not self.verify_token():
                self.get_token()
        except (IOError, FileNotFoundError):
            self.get_token()

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

        If the token is bad or if the expiration time is less than the
        threshold False will be returned.

        """
        resp = requests.get(self.api_url + '/session',
                            headers={self.token['name']: self.token['value']},
                            verify=True)
        resp.raise_for_status()

        json_resp = resp.json()

        if json_resp['name'] is None:
            return False
        elif json_resp['expires_in'] / 60.0 < self.token_expiration_threshold:
            return False
        else:
            return True
