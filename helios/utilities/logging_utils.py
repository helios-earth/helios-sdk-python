"""Utility functions for logging."""
import collections
import functools
import json
import logging.config
import os


def configure_logger():
    """
    Configures the logger.

    If a configuration file does not exist in the root user directory, then
    default configuration options will be written to file.  This file can be
    customized and will be read on the next configuration.

    """
    # Attempt to read SDK logging config file
    config_file = os.path.join(os.path.expanduser('~'), '.helios', 'logger.json')

    config = None
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
        except ValueError:
            config = None

    if config is None:
        # Default logging configuration.
        config = collections.defaultdict(dict)

        config['version'] = 1
        config['disable_existing_loggers'] = 1

        config['formatters']['simple'] = {'format': '%(asctime)s-%(levelname)s'
                                                    '-%(module)s-%(name)s'
                                                    '-%(funcName)s: %(message)s',
                                          'datefmt': '%H:%M:%S'}

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


def log_entrance_exit(func):
    """
    Decorator to log the entrance and exit of method calls.

    This will make use of the logger instance passed via self.  When using
    functools.wraps, self will be the first index in args.
    See self = args[0] comment below.

    Args:
        func: The function to be wrapped.

    Returns:
        Wrapped function.

    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # self should be first argument.
        func_self = args[0]
        if len(args) > 1:
            func_self._logger.info('Entering %s: %s, %s', func.__name__, args[1:], kwargs)
        else:
            func_self._logger.info('Entering %s: %s', func.__name__, kwargs)

        # Evaluate wrapped function.
        f_result = func(*args, **kwargs)

        if len(args) > 1:
            func_self._logger.info('Exiting %s: %s, %s', func.__name__, args[1:], kwargs)
        else:
            func_self._logger.info('Exiting %s: %s', func.__name__, kwargs)
        return f_result

    return wrapper
