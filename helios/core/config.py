"""Handle SDK configuration parameters."""
import os

config = {}


def load_config():
    """Loads configuration from environment variables."""

    global config
    config['max_concurrency'] = int(os.environ.get('max_concurrency', 500))
    config['ssl_verify'] = bool(os.environ.get('ssl_verify', True))
    config['token_expiration_threshold'] = int(
        os.environ.get('token_expiration_threshold', 60))
