"""
SDK for the Helios Alerts API.

Methods are meant to represent the core functionality in the developer
documentation.  Some may have additional functionality for convenience.

"""
import logging

from heliosSDK.core import SDKCore, IndexMixin, ShowMixin, RequestManager


class Alerts(ShowMixin, IndexMixin, SDKCore):
    core_api = 'alerts'
    max_threads = 32

    def __init__(self):
        self.request_manager = RequestManager(pool_maxsize=self.max_threads)
        self.logger = logging.getLogger(__name__)

    def index(self, **kwargs):
        return super(Alerts, self).index(**kwargs)

    def show(self, alert_id):
        return super(Alerts, self).show(alert_id)
