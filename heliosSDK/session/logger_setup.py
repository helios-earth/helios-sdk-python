"""Configure the logger based on a file or standard parameters."""
import json
import logging.config
import os


def configure():
    """
    Configures the logger.

    If a configuration file does not exist in the root user directory, then
    default configuration options will be written to file.  This file can be
    customized and will be read on the next configuration.

    """
    # Attempt to read SDK logging config file
    config_file = os.path.join(os.path.expanduser('~'),
                               'heliosSDK_logger_config.json')
    config = None
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
        except ValueError:
            config = None

    if config is None:
        # Default logging configuration.
        config = {'version': 1, 'disable_existing_loggers': 1}

        config['formatters'] = {}
        config['formatters']['simple'] = {'format': '%(asctime)s-%(levelname)s'
                                                    '-%(module)s-%(name)s'
                                                    '-%(funcName)s: %(message)s',
                                          'datefmt': '%H:%M:%S'}

        config['handlers'] = {}
        config['handlers']['console'] = {'class': 'logging.StreamHandler',
                                         'level': 'WARNING',
                                         'formatter': 'simple',
                                         'stream': 'ext://sys.stdout'}

        config['root'] = {'level': 'INFO',
                          'handlers': ['console']}

        # Write default configuration to file
        try:
            with open(config_file, 'w') as f:
                json.dump(config, f)
        except IOError:
            pass

    logging.config.dictConfig(config)
