"""Utility functions for logging."""
import functools


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
