"""
SDK for the Helios Alerts API.

Methods are meant to represent the core functionality in the developer documentation.  Some may have additional
functionality for convenience.

"""
import logging

from heliosSDK.core import SDKCore, IndexMixin, ShowMixin, RequestManager


class Alerts(ShowMixin, IndexMixin, SDKCore):
    CORE_API = 'alerts'
    MAX_THREADS = 32

    def __init__(self):
        self.requestManager = RequestManager(pool_maxsize=self.MAX_THREADS)
        self.logger = logging.getLogger(__name__)

    def index(self, **kwargs):
        return super(Alerts, self).index(**kwargs)

    def show(self, alert_id):
        return super(Alerts, self).show(alert_id)
