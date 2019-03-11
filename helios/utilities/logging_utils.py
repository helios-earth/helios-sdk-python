"""Utility functions for logging."""
import functools
import logging.config
from timeit import default_timer as timer

logger = logging.getLogger(__name__)


def log_entrance_exit(func):
    """
    Decorator to log the entrance and exit of method calls.

    Args:
        func: The function to be wrapped.

    Returns:
        Wrapped function.

    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        logger.info('Entering %s', func.__name__)

        # Evaluate wrapped function.
        t0 = timer()
        try:
            f_result = func(*args, **kwargs)
        except Exception:
            logger.exception('Unhandled exception occurred.')
            raise

        logger.info('Exiting %s [%s]', func.__name__, '{0:.4f}s'.format(timer() - t0))

        return f_result

    return wrapper
