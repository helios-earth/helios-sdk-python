"""Handle SDK configuration parameters."""
import logging
import os

logger = logging.getLogger(__name__)

config = {}


def _handle_bool_env(value):
    """
    Handles an environment variables that should correspond to True/False.

    Args:
        value (str): Environment variable.

    Returns:
        bool or None: The corresponding boolean value for the variable. Can also
            return None if that is what is found.

    Raises:
        ValueError: If value can not be converted properly.

    """

    if value.lower() == 'true':
        return True
    elif value.lower() == 'false':
        return False
    elif value == '0':
        return False
    elif value == '1':
        return True
    elif value.lower() == 'none':
        return None
    else:
        raise ValueError()


def load_config():
    """Loads configuration from environment variables."""

    global config

    try:
        ssl_verify = _handle_bool_env(os.environ.get('ssl_verify', '1'))
    except ValueError:
        logger.exception('Could not load "ssl_verify" from env variables. '
                         'Make sure value is "1", "0", "False", or "True"')
        raise

    config['max_concurrency'] = int(os.environ.get('max_concurrency', 500))
    config['ssl_verify'] = ssl_verify
    config['token_expiration_threshold'] = int(
        os.environ.get('token_expiration_threshold', 60))
