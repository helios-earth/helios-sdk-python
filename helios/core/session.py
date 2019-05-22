"""Manager for the authorization token required to access the Helios API."""
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path

import requests

import helios

logger = logging.getLogger(__name__)

_DEFAULT_API_URL = 'https://api.helios.earth/v1'


class Authentication:
    """
    Authentication API.

    Args:
        client_id (str): API key ID.
        client_secret (str): API key secret.
        api_url (str): Override the default API URL.

    """

    def __init__(self, client_id, client_secret, api_url=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_url = api_url or _DEFAULT_API_URL

        # To be safe.
        self.api_url = self.api_url.rstrip('/')

    def get_access_token(self):
        """
        Gets a new access token.

        Returns:
            Token: Helios API access token.

        """

        logger.info('Acquiring a new token.')

        token_url = self.api_url + '/oauth/token'
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }

        try:
            resp = requests.post(token_url, json=data)
            resp.raise_for_status()
        except Exception:
            logger.exception('Failed to acquire token.')
            raise

        json_resp = resp.json()

        logger.info('Successfully acquired a new token.')

        return Token(**json_resp)

    def get_current_user(self, token):
        """
        Return a compact list of current token attributes, such as the
        token expiration date.

        Args:
            token (Token): A Helios Token.

        Returns:
            dict: Token attributes.

        Raises:
            ValueError: If current token is invalid or expired.

        """

        url = self.api_url + '/session'

        try:
            resp = requests.get(url, headers=token.auth_header)
            resp.raise_for_status()
        except Exception:
            logger.exception('Failed to get token expiration time.')
            raise

        json_resp = resp.json()

        if json_resp['name'] is None:
            _msg = 'Token appears to be invalid or expired.'
            logger.error(_msg)
            raise ValueError(_msg)

        return json_resp


class Token:
    """
    Helios token.

    Args:
        access_token (str): Access token.
        expires_in (int): Seconds until expiration. WARNING: this value can be
            misleading.  If reading from a token file the value will not be
            current.
        kwargs: Any other optional token attributes.

    """

    def __init__(self, access_token, expires_in=None, **kwargs):
        self.access_token = access_token
        self._expires_in = expires_in

        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def auth_header(self):
        """Authentication header for API requests."""
        try:
            return {'Authorization': 'Bearer ' + self.access_token}
        except KeyError:
            logger.error('A token must be acquired to establish an auth header.')
            raise

    @property
    def expired(self):
        """True if token is expired, False otherwise."""
        now = datetime.now()
        if now >= self.expiration:
            return True
        else:
            return False

    @property
    def expiration(self):
        """The expiration time."""
        now = datetime.now()
        delta = timedelta(seconds=self._expires_in)
        return now + delta

    def to_json(self):
        """
        Serializes token to JSON.

        Returns:
            str: JSON serialized string.

        """

        output_dict = {
            k: v for k, v in vars(self).items() if not k.startswith(('_', '__'))
        }

        return json.dumps(output_dict, skipkeys=True)


class HeliosSession:
    """
    Manages configuration and authentication details for the Helios APIs.

    The session will handle acquiring and verifying tokens as well as various
    developer options.

    Args:
        client_id (str, optional): API key ID.
        client_secret (str, optional): API key secret.
        api_url (str, optional): Override the default API URL.
        base_directory (str, optional): Override the base directory for
            storage of tokens and credentials.json file.
        max_threads (int, optional): The maximum number of threads allowed for
            batch calls.
        token_expiration_threshold (int, optional): The number of minutes
            to allow before token expiration.  E.g. if the token will expire
            in 29 minutes and the threshold is set to 30, a new token will
            be acquired because expiration time is below the threshold.
        ssl_verify (bool, optional): Use SSL verification for all HTTP
            requests.  Defaults to True.

    """

    def __init__(
        self,
        client_id=None,
        client_secret=None,
        api_url=None,
        base_directory=None,
        max_threads=64,
        token_expiration_threshold=60,
        ssl_verify=True,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_url = api_url
        self.max_threads = max_threads
        self.ssl_verify = ssl_verify

        self._token_expiration_threshold = token_expiration_threshold
        self._base_directory = base_directory

        # Handle optional parameter settings.
        if self._base_directory is None:
            self._base_directory = Path.home() / '.helios'
        else:
            self._base_directory = Path(self._base_directory)

        if self.api_url is None:
            self.api_url = _DEFAULT_API_URL
        else:
            self.api_url = self.api_url.rstrip('/')

        if None in (self.client_id, self.client_secret):
            self._get_credentials()

        # Create token filename based on authentication ID.
        self._token_dir = self._base_directory / '.tokens'
        self._token_file = self._token_dir / (self.client_id + '.helios_token')

        # Create an instances of the auth API.
        self.auth_api = Authentication(
            self.client_id, self.client_secret, api_url=self.api_url
        )

        # Establish self.token.
        try:
            self.read_token()
        except (IOError, OSError):
            logger.warning(
                'Could not read token file (%s). A new token will be acquired.',
                self._token_file,
            )
            self.get_new_token()
        except (ValueError, KeyError, TypeError):
            logger.warning(
                'Token was invalid or expired. A new token will be ' 'acquired.'
            )
            self.get_new_token()

    @property
    def auth_header(self):
        """Authentication header for API requests."""
        self.verify_token()

        return self.token.auth_header

    def _get_credentials(self):
        """Handles the various methods for referencing API credentials."""

        credentials_file = self._base_directory / 'credentials.json'

        if 'helios_client_id' in os.environ and 'helios_client_secret' in os.environ:
            logger.info('Credentials found in environment variables.')
            data = os.environ
        elif credentials_file.exists():
            logger.info('Credentials found in file: %s', str(credentials_file))
            with open(credentials_file, mode='r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            raise Exception(
                'No credentials could be found. Be sure to '
                'set environment variables or create a '
                'credentials file.'
            )
        self.client_id = data['helios_client_id']
        self.client_secret = data['helios_client_secret']
        if self.api_url is None:
            self.api_url = data.get('helios_api_url')

    def read_token(self):
        """Reads token from file."""

        logger.info('Reading token from file: %s', self._token_file)

        with open(self._token_file, mode='r', encoding='utf-8') as f:
            contents = json.loads(f.read())
            token = Token(**contents)
            # Must get the real expires_in value when reading from an old file.
            real_expiration = self.auth_api.get_current_user(token)['expires_in']
            token._expires_in = real_expiration

        self.token = token

    def write_token(self):
        """Writes token to file."""

        logger.info('Writing token to file: %s', self._token_file)

        if not self._token_file.parent.exists():
            self._token_file.parent.mkdir(parents=True)

        try:
            with open(self._token_file, mode='w', encoding='utf-8') as f:
                f.write(self.token.to_json())
        except Exception:
            # Prevent a bad token file from persisting after an exception.
            if self._token_file.exists():
                self._token_file.unlink()
            raise

    def verify_token(self):
        """
        Verifies that token has not expired.

        If the token has expired a new token will be acquired.

        """

        if self.token.expired:
            logger.info('Token has expired.')
            self.get_new_token()

    def get_new_token(self):
        """Gets a new token for the current Helios session."""

        logger.info('Getting a new token.')
        self.token = self.auth_api.get_access_token()
        self.write_token()

    def client(self, name):
        """
        Gets a core API instance using the current HeliosSession.

        Args:
            name (str): Name of API.

        Returns:
            Core API instance.

        """

        self.verify_token()

        return helios.__APIS__[name.lower()](session=self)
