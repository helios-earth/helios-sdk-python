"""Manager for the authorization token required to access the Helios API."""
import asyncio
import json
import logging
import os

import aiofiles
import aiohttp

logger = logging.getLogger(__name__)

# Defaults
_DEFAULT_API_URL = r'https://api.helios.earth/v1'
_DEFAULT_BASE_DIR = os.path.join(os.path.expanduser('~'), '.helios')


class HeliosSession:
    """
    Handles parameters for Helios APIs.

    The Helios session supports the context manager protocol for initiating
    a session:

    .. code-block:: python3

        import helios
        async with helios.HeliosSession() as sess:
            alerts_inst = helios.Alerts(sess)

    Also, for creating and storing a session instance:

    .. code-block:: python3

        import helios
        sess = helios.HeliosSession()
        await sess.start_session() # Must manually start the session.
        alerts_inst = helios.Alerts(sess)

    Args:
        client_id (str, optional): API key ID.
        client_secret (str, optional): API key secret.
        api_url (str, optional): Override the default API URL.
        base_directory (str, optional): Override the base directory for
            storage of tokens and credentials.json file.
        max_concurrency (int, optional): The maximum concurrency allowed for
            batch calls. Defaults to 500.
        token_expiration_threshold (int, optional): The number of minutes
            to allow before token expiration.  E.g. if the token will expire
            in 29 minutes and the threshold is set to 30, a new token will
            be acquired because expiration time is below the threshold.
        ssl_verify (bool, optional): Use SSL verification for all HTTP
            requests.  Defaults to True.

    Attributes:
        auth_header (dict): Authentication header for HTTP requests.
        token (dict): API token.
        client_id (str): API key ID.
        client_secret (str): API key secret.
        api_url (str): API URL.
        max_concurrency (int): Maximum concurrency allowed.

    """

    def __init__(
        self,
        client_id=None,
        client_secret=None,
        api_url=None,
        base_directory=None,
        max_concurrency=500,
        token_expiration_threshold=60,
        ssl_verify=True,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_url = api_url
        self.max_concurrency = max_concurrency
        self.ssl_verify = ssl_verify

        self._token_expiration_threshold = token_expiration_threshold
        self._base_directory = base_directory

        # The following will be established upon entering a session.
        self.auth_header = None
        self.token = None
        self._token_file = None
        self._token_dir = None

        if self._base_directory is None:
            self._base_directory = _DEFAULT_BASE_DIR

        if None in (self.client_id, self.client_secret):
            self._get_credentials()

        if self.api_url is None:
            self.api_url = _DEFAULT_API_URL
        else:
            self.api_url = self.api_url.rstrip('/')

        # Create async semaphore for concurrency limit.
        self.async_semaphore = asyncio.Semaphore(value=self.max_concurrency)

    def _get_credentials(self):
        """Handles the various methods for referencing API credentials."""
        if self._base_directory is None:
            self._base_directory = _DEFAULT_BASE_DIR

        if 'helios_client_id' in os.environ and 'helios_client_secret' in os.environ:
            logger.info('Credentials found in environment variables.')
            data = os.environ
        elif os.path.exists(os.path.join(self._base_directory, 'credentials.json')):
            self._credentials_file = os.path.join(
                self._base_directory, 'credentials.json'
            )
            logger.info('Credentials found in credentials.json file.')
            with open(self._credentials_file, 'r') as f:
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

    async def _read_token(self):
        """Reads token from file."""
        async with aiofiles.open(self._token_file, mode='r') as f:
            self.token = json.loads(await f.read())

    async def _write_token(self):
        """Writes token to file."""
        if not os.path.exists(self._token_dir):
            os.makedirs(self._token_dir)
        try:
            async with aiofiles.open(self._token_file, mode='w') as f:
                await f.write(json.dumps(self.token))
        except Exception:
            # Prevent a bad token file from persisting after an exception.
            if os.path.exists(self._token_file):
                os.remove(self._token_file)
            raise

    async def _get_new_token(self):
        """
        Gets a fresh token and saves it.

        The token will be acquired and then written to file for reuse. If the
        request fails over https, http will be used as a fallback.

        """
        logger.info('Acquiring a new token.')

        token_url = self.api_url + '/oauth/token'
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret,
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    token_url, data=data, ssl=self.ssl_verify, raise_for_status=True
                ) as resp:
                    json_resp = await resp.json()
            except Exception:
                logger.exception('Failed to acquire token.')
                raise

        self.token = {
            'name': 'Authorization',
            'value': 'Bearer ' + json_resp['access_token'],
        }

        await self._write_token()

        logger.info('Successfully acquired new token.')

    async def verify_token(self):
        """
        Verifies the token.

        If the token is bad or if the expiration time is less than the
        threshold False will be returned.

        Returns:
            bool: True if current token is valid, False otherwise.

        """

        auth_header = {self.token['name']: self.token['value']}
        verify_url = self.api_url + '/session'
        async with aiohttp.ClientSession(headers=auth_header) as session:
            try:
                async with session.get(verify_url, ssl=self.ssl_verify) as resp:
                    json_resp = await resp.json()
            except Exception:
                logger.exception('Failed to verify token.')
                raise

        if not json_resp['name'] or not json_resp['expires_in']:
            return False

        # Check token expiration time.
        expiration = json_resp['expires_in'] / 60.0
        if expiration < self._token_expiration_threshold:
            logger.warning(
                'Token expiration (%d) is less than the threshold (%d).',
                expiration,
                self._token_expiration_threshold,
            )
            return False

        logger.info('Token is valid for %d minutes.', expiration)

        return True

    async def start_session(self):
        """Starts the Helios session by finding a token."""

        # Create token filename based on authentication ID.
        self._token_dir = os.path.join(self._base_directory, '.tokens')
        self._token_file = os.path.join(
            self._token_dir, self.client_id + '.helios_token'
        )

        try:
            await self._read_token()
        except (IOError, OSError):
            logger.warning(
                'Could not read token file (%s). A new token will be acquired.',
                self._token_file,
            )
            await self._get_new_token()
        else:
            if not await self.verify_token():
                await self._get_new_token()

        self.auth_header = {self.token['name']: self.token['value']}

    def __enter__(self) -> None:
        raise TypeError("Use async with instead")

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    async def __aenter__(self):
        if self.token is None:
            await self.start_session()

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass
