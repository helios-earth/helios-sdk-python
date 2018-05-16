import json
import logging
import os

logger = logging.getLogger(__name__)

_DEFAULT_CONFIG = {'GENERAL': {'MAX_THREADS': 32},
                   'REQUESTS': {'RETRIES': 3,
                                'TIMEOUT': 5,
                                'SSL_VERIFY': True},
                   'SESSION': {'TOKEN_EXPIRATION_THRESHOLD': 60}}


class Config(dict):
    """
    Dictionary-like object for storing configuration parameters.

    If the config file does not exist it will be written with defaults to the
    default location.

    If the config file exists the default values will be updated with the
    values contained in the config file.

    """

    _config_file = os.path.join(os.path.expanduser('~'), '.helios', 'config.json')

    def __init__(self):
        super(Config, self).__init__(_DEFAULT_CONFIG)
        self._setup()

    def _read_config_file(self):
        """Loads configuration file from default location."""
        try:
            with open(self._config_file, 'r') as f:
                config = json.load(f)
        except Exception:
            logger.exception('Failed to read configuration file.')
            raise
        else:
            return config

    def _write_default_config_file(self):
        """Writes configuration JSON dict to file."""
        try:
            with open(self._config_file, 'w') as f:
                json.dump(_DEFAULT_CONFIG, f)
        except Exception:
            logger.exception('Failed to write configuration file.')
            raise

    def _setup(self):
        """Establishes configuration values."""
        try:
            config = self._read_config_file()
        except Exception:
            self._write_default_config_file()
        else:
            self.update(config)


CONFIG = Config()
