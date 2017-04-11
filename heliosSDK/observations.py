'''
SDK for the Helios Observations API.  Methods are meant to represent the core
functionality in the developer documentation.  Some may have additional
functionality for convenience.  

@author: mbayer
'''
import os
from heliosSDK import AUTH_TOKEN
from heliosSDK.core import SDKCore, IndexMixin, ShowMixin, DownloadImagesMixin
import json
import skimage.io
from io import BytesIO
import warnings


class Observations(DownloadImagesMixin, ShowMixin, IndexMixin, SDKCore):
    _CORE_API = 'observations'
    
    def __init__(self):
        pass

    def index(self, **kwargs):
        return super(Observations, self).index(**kwargs)
    
    def show(self, observation_id):
        return super(Observations, self).show(observation_id) 
    
    def preview(self, observation_id):
        query_str = '{}/{}/{}/preview'.format(self._BASE_API_URL,
                                        self._CORE_API,
                                        observation_id)
        resp = self._getRequest(query_str,
                               headers={AUTH_TOKEN['name']:AUTH_TOKEN['value']},
                               verify=self._SSL_VERIFY) 
        
        redirect_url = resp.url[0:resp.url.index('?')]
        
        # Check header for dud statuses. 
        head_check_resp = self._headRequest(redirect_url)
        if 'x-amz-meta-helios' in head_check_resp.headers:
            hdrs = json.loads(head_check_resp.headers['x-amz-meta-helios'])
            
            if hdrs['isOutcast'] or hdrs['isDud'] or hdrs['isFrozen']:
                warnings.warn('{} returned a dud image.'.format(redirect_url))
                return {'url' : None}

        return {'url' : redirect_url}
            
    def downloadImages(self, urls, out_dir=None, return_image_data=False):
        return super(Observations, self).downloadImages(urls, out_dir=out_dir, return_image_data=return_image_data)













