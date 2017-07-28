'''
SDK for the Helios Alerts API.  Methods are meant to represent the core
functionality in the developer documentation.  Some may have additional
functionality for convenience.  

@author: Michael A. Bayer
'''
from heliosSDK.core import SDKCore, IndexMixin, ShowMixin


class Alerts(ShowMixin, IndexMixin, SDKCore):
    MAX_THREADS = 20
    
    _CORE_API = 'alerts'
    
    def __init__(self):
        pass
        
    def index(self, **kwargs):
        return super(Alerts, self).index(**kwargs)
    
    def show(self, alert_id):
        return super(Alerts, self).show(alert_id)