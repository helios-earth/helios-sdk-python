"""Use the Helios APIs in Python"""
from . import core
from . import utilities
from .alerts_api import Alerts
from .cameras_api import Cameras
from .collections_api import Collections
from .core.session import Session
from .observations_api import Observations
# Configure logger.
from .utilities.logging_utils import configure_logger

configure_logger()

# Cleanup
del configure_logger

__version__ = '2.2.0'
