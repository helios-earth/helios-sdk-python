import json
import os

try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping

_CONFIG_FILE = os.path.join(os.path.expanduser('~'), '.helios', 'config.json')
_CONFIG_DEFAULTS = {'general': {'max_threads': 32},
                    'requests': {'retries': 3,
                                 'timeout': 5,
                                 'ssl_verify': True},
                    'session': {'token_expiration_threshold': 60}}


def write_default_config_file():
    """Writes the default configuration to the default file."""
    with open(_CONFIG_FILE, 'w') as f:
        json.dump(_CONFIG_DEFAULTS, f)


class Config(Mapping):
    """
    Mapping object for storing configuration parameters in a dict-like interface.

    If the config file does not exist it will be written with defaults to the
    default location.

    If the config file exists the default values will be updated with the
    values contained in the config file.

    """

    def __init__(self):
        self.__dict__ = _CONFIG_DEFAULTS
        self._load_config()

    def __getitem__(self, key):
        return self.__dict__[key]

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __repr__(self):
        return self.__dict__.__repr__()

    @staticmethod
    def _read_config_file():
        """Reads configuration file."""
        with open(_CONFIG_FILE, 'r') as f:
            config = json.load(f)
        return config

    def _load_config(self):
        """Loads the configuration parameters."""
        try:
            config = self._read_config_file()
        except (IOError, OSError):
            if not os.path.exists(_CONFIG_FILE):
                write_default_config_file()
            else:
                raise
        else:
            self.__dict__.update(config)


CONFIG = Config()
