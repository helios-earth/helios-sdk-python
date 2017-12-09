"""Utility functions for logging."""
import functools


def log_entrance_exit(func):
    """
    Decorate a method to log the entrance and exit.

    This will make use of the logger instance passed via self.  When using
    functools.wraps, self will be the first index in args.
    See self = args[0] comment below.

    :param func:
    :return: evaluated function results
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # self should be first argument.
        func_self = args[0]
        if len(args) > 1:
            func_self.logger.info('Entering %s: %s, %s', func.__name__, args[1:], kwargs)
        else:
            func_self.logger.info('Entering %s: %s', func.__name__, kwargs)

        # Evaluate wrapped function.
        f_result = func(*args, **kwargs)

        if len(args) > 1:
            func_self.logger.info('Exiting %s: %s, %s', func.__name__, args[1:], kwargs)
        else:
            func_self.logger.info('Exiting %s: %s', func.__name__, kwargs)
        return f_result

    return wrapper
