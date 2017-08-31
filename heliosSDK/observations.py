'''
SDK for the Helios Observations API.  Methods are meant to represent the core
functionality in the developer documentation.  Some may have additional
functionality for convenience.  

@author: mbayer
'''
from heliosSDK.core import SDKCore, IndexMixin, ShowMixin, DownloadImagesMixin
from heliosSDK.utilities import jsonTools
import json
import logging
from multiprocessing.dummy import Pool as ThreadPool
import os
import sys


class Observations(DownloadImagesMixin, ShowMixin, IndexMixin, SDKCore):
    MAX_THREADS = 20

    _CORE_API = 'observations'
        
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def index(self, **kwargs):
        return super(Observations, self).index(**kwargs)
    
    def show(self, observation_id):
        return super(Observations, self).show(observation_id)
    
    def preview(self, observation_ids):
        if not isinstance(observation_ids, list):
            observation_ids = [observation_ids]
            
        # Log entrance
        self.logger.info('Entering preview({} observation_ids)'.format(len(observation_ids)))
                         
        # Get number of threads
        num_threads = min(self.MAX_THREADS, len(observation_ids))
        
        # Process ids.
        if num_threads > 4:
            POOL = ThreadPool(num_threads)
            data = POOL.map(self.__previewWorker, observation_ids)
        else:
            data = map(self.__previewWorker, observation_ids)
            
        # Remove errors, if they exist
        data = [x for x in data if x is not None]
        
        # Log success
        self.logger.info('Leaving preview({} out of {} successful)'.format(len(data), len(observation_ids)))
        
        urls = jsonTools.mergeJson(data, 'url')
        
        return {'url' : urls}                                  
    
    def __previewWorker(self, args):
        observation_id = args
                
        query_str = '{}/{}/{}/preview'.format(self._BASE_API_URL,
                                        self._CORE_API,
                                        observation_id)
        
        # Log query
        self.logger.info('Query began: {}'.format(query_str))
        
        resp = self._getRequest(query_str,
                               headers={self._AUTH_TOKEN['name']:self._AUTH_TOKEN['value']},
                               verify=self._SSL_VERIFY)
        
        # Log error and raise exception.
        if not resp.ok:
            self.logger.error('Error {}: {}'.format(resp.status_code, query_str))
            return None
            
        redirect_url = resp.url[0:resp.url.index('?')]
        
        # Check header for dud statuses. 
        head_check_resp = self._headRequest(redirect_url)
        if 'x-amz-meta-helios' in head_check_resp.headers:
            hdrs = json.loads(head_check_resp.headers['x-amz-meta-helios'])
            
            if hdrs['isOutcast'] or hdrs['isDud'] or hdrs['isFrozen']:
                sys.stderr.write('{} returned a dud image.'.format(redirect_url) + os.linesep)
                sys.stderr.flush()
                return {'url' : None}
        
        # Log success
        self.logger.info('Query complete: {}'.format(query_str))

        return {'url' : redirect_url}
                            
    def downloadImages(self, urls, out_dir=None, return_image_data=False):
        return super(Observations, self).downloadImages(urls, out_dir=out_dir, return_image_data=return_image_data)










