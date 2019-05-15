"""Use the Helios APIs in Python"""
import logging

from . import core
from . import utilities
from .alerts_api import Alerts
from .cameras_api import Cameras
from .collections_api import Collections
from .observations_api import Observations
from .core.session import HeliosSession

__APIS__ = {
    'alerts': alerts_api.Alerts,
    'cameras': cameras_api.Cameras,
    'collections': collections_api.Collections,
    'observations': observations_api.Observations,
}

DEFAULT_HELIOS_SESSION = None


def _get_default_session(**kwargs):
    """Gets the default HeliosSession."""

    global DEFAULT_HELIOS_SESSION
    if DEFAULT_HELIOS_SESSION is None:
        DEFAULT_HELIOS_SESSION = HeliosSession(**kwargs)

    return DEFAULT_HELIOS_SESSION


def add_stderr_logger(level=logging.DEBUG):
    """
    Helper for quickly adding a StreamHandler to the logger. Useful for
    debugging.

    Follows urllib3 implementation.

    Returns the handler after adding it.

    """
    # This method needs to be in this __init__.py to get the __name__ correct
    # even if helios is vendored within another package.
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(fmt='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    )
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.debug('Added a stderr logging handler to logger: %s', __name__)
    return handler


def client(name):
    """
    Gets a core API instance using the default HeliosSession.

    Args:
        name (str): Name of API.

    Returns:
        Core API instance.

    """
    return _get_default_session().client(name)


__version__ = '3.0.1'
