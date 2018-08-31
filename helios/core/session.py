"""Manager for the authorization token required to access the Helios API."""
import json
import logging
import os
import tempfile

import requests

from helios import CONFIG

logger = logging.getLogger(__name__)


class Session(object):
    """Manages API tokens for authentication.

    Authentication credentials can be specified using the env input parameter,
    environment variables, or a credentials.json file in your ~/.helios
    directory.  See the official documentation for more authentication
    information.

    Required keys:
        - helios_client_id: Client ID from API key pair.
        - helios_client_secret: Client Secret ID from API key pair.
    Optional keys:
        - helios_api_url: Optional, URL for API endpoint.

    A session can be established and reused for multiple core API instances.

    .. code-block:: python

        import helios
        sess = helios.Session()
        alerts = helios.Alerts(session=sess)
        cameras = helios.Cameras(session=sess)

    If a session is not specified before hand, one will be initialized
    automatically.  This is less efficient because each core API instance
    will try to initialize a session.

    .. code-block:: python

        import helios
        alerts = helios.Alerts()
        cameras = helios.Cameras()

    """

    ssl_verify = CONFIG['requests']['ssl_verify']
    token_expiration_threshold = CONFIG['session']['token_expiration_threshold']

    _default_api_url = r'https://api.helios.earth/v1'

    def __init__(self, env=None):
        """Initialize Helios Session.

        Args:
            env (dict): Dictionary containing 'helios_client_id',
                'helios_client_secret', and optionally 'helios_api_url'.
                This will override any information in credentials.json and
                environment variables.

        """
        # Establish necessary files/directories.
        self._base_dir = None
        self._credentials_file = None
        self._token_dir = None
        self._verify_directories()

        # The token will be established with a call to the start_session method.
        self.token = None

        # Use custom credentials.
        if env is not None:
            logger.info('Using custom env for session.')
            data = env
        # Read credentials from environment.
        elif 'helios_client_id' in os.environ and 'helios_client_secret' in os.environ:
            logger.info('Using environment variables for session.')
            data = os.environ
        # Read credentials from file.
        elif os.path.exists(self._credentials_file):
            logger.info('Using credentials file for session.')
            with open(self._credentials_file, 'r') as auth_file:
                data = json.load(auth_file)
        else:
            raise Exception('No credentials could be found. Be sure to '
                            'set environment variables or create a '
                            'credentials file.')

        # Extract relevant authentication information from data.
        self._key_id = data['helios_client_id']
        self._key_secret = data['helios_client_secret']
        self.api_url = data.get('helios_api_url') or self._default_api_url
        self.api_url = self.api_url.rstrip('/')

        # Create token filename based on authentication ID.
        self._token_file = os.path.join(self._token_dir,
                                        self._key_id + '.helios_token')

        # Finally, start the session.
        self.start_session()

    def _delete_token(self):
        """Deletes token file."""
        os.remove(self._token_file)

    def _get_token(self):
        """
        Gets a fresh token.

        The token will be acquired and then written to file for reuse. If the
        request fails over https, http will be used as a fallback.

        """
        logger.info('Acquiring a new token.')

        token_url = self.api_url + '/oauth/token'
        data = {'grant_type': 'client_credentials'}
        auth = (self._key_id, self._key_secret)
        try:
            resp = requests.post(token_url, data=data, auth=auth,
                                 verify=self.ssl_verify)
            resp.raise_for_status()
        except requests.exceptions.HTTPError:
            logger.warning('Getting token over https failed. Falling back to http.',
                           exc_info=True)
            resp = requests.post(token_url.replace('https', 'http'), data=data,
                                 auth=auth, verify=self.ssl_verify)

        # If the token cannot be acquired raise exception.
        try:
            resp.raise_for_status()
        except requests.exceptions.RequestException:
            logger.exception('Failed to acquire token.')
            raise

        token_request = resp.json()
        self.token = {'name': 'Authorization',
                      'value': 'Bearer ' + token_request['access_token']}

        logger.info('Successfully acquired new token.')

    def _read_token_file(self):
        """Reads token from file."""
        with open(self._token_file, 'r') as token_file:
            self.token = json.load(token_file)

    def _verify_directories(self):
        """Verifies essential directories."""

        # Explicitly check for write capability.
        # Provides a fall back to the default temp directory.
        base_dir = os.path.join(os.path.expanduser('~'), '.helios')
        write_test_file = os.path.join(base_dir, 'temp_file.tmp')
        try:
            if os.path.exists(base_dir):
                with open(write_test_file, 'w+') as _:
                    pass
            else:
                os.makedirs(base_dir)
        except (IOError, OSError):
            base_dir = tempfile.gettempdir()
        finally:
            if os.path.exists(write_test_file):
                os.remove(write_test_file)

        # Establish paths.
        self._base_dir = base_dir
        self._token_dir = os.path.join(self._base_dir, '.tokens')
        self._credentials_file = os.path.join(self._base_dir, 'credentials.json')

        if not os.path.exists(self._base_dir):
            os.makedirs(self._base_dir)

        if not os.path.exists(self._token_dir):
            os.makedirs(self._token_dir)

    def _write_token_file(self):
        """Writes token to file."""
        try:
            with open(self._token_file, 'w+') as token_file:
                json.dump(self.token, token_file)
        except Exception:
            # Prevent a bad token file from persisting after an exception.
            if os.path.exists(self._token_file):
                os.remove(self._token_file)
            raise

    def start_session(self):
        """
        Begins Helios session.

        This will establish and verify a token for the session.  If a token
        file exists the token will be read and verified. If the token file
        doesn't exist or the token has expired then a new token will be
        acquired.

        """
        try:
            self._read_token_file()
        except (IOError, OSError):
            logger.warning('Could not read token (%s). A new token will be acquired.',
                           self._token_file)
            self._get_token()
        else:
            if not self.verify_token():
                self._get_token()

        self._write_token_file()

    def verify_token(self):
        """
        Verifies the token.

        If the token is bad or if the expiration time is less than the
        threshold False will be returned.

        Returns:
            bool: True if current token is valid, False otherwise.

        """
        resp = requests.get(self.api_url + '/session',
                            headers={self.token['name']: self.token['value']},
                            verify=self.ssl_verify)

        # If the token cannot be verified raise exception.
        try:
            resp.raise_for_status()
        except requests.exceptions.RequestException:
            logger.exception('Failed to verify token.')
            raise

        json_resp = resp.json()

        if not json_resp['name'] or not json_resp['expires_in']:
            return False

        # Check token expiration time.
        expiration = json_resp['expires_in'] / 60.0
        if expiration < self.token_expiration_threshold:
            logger.warning('Token expiration (%d) is less than the threshold (%d).',
                           expiration,
                           self.token_expiration_threshold)
            return False

        logger.info('Token is valid for %d minutes.', expiration)

        return True
