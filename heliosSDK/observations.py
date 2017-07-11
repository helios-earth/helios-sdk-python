'''
SDK for the Helios Observations API.  Methods are meant to represent the core
functionality in the developer documentation.  Some may have additional
functionality for convenience.  

@author: mbayer
'''
import json
import os
import sys
from threading import Thread
import traceback

from heliosSDK.core import SDKCore, IndexMixin, ShowMixin, DownloadImagesMixin
from heliosSDK.utilities import jsonTools


# Python 2 and 3 fixes
try:
    from Queue import Queue
except ImportError:
    from queue import Queue
    
try:
    import thread
except ImportError:
    import _thread as thread


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
                               headers={self._AUTH_TOKEN['name']:self._AUTH_TOKEN['value']},
                               verify=self._SSL_VERIFY) 
        
        redirect_url = resp.url[0:resp.url.index('?')]
        
        # Check header for dud statuses. 
        head_check_resp = self._headRequest(redirect_url)
        if 'x-amz-meta-helios' in head_check_resp.headers:
            hdrs = json.loads(head_check_resp.headers['x-amz-meta-helios'])
            
            if hdrs['isOutcast'] or hdrs['isDud'] or hdrs['isFrozen']:
                sys.stderr.write('{} returned a dud image.'.format(redirect_url) + os.linesep)
                sys.stderr.flush()
                return {'url' : None}

        return {'url' : redirect_url}
    
    def previews(self, observation_ids):
        if not isinstance(observation_ids, list):
            observation_ids = [observation_ids]
            
        # Set up the queue
        q = Queue(maxsize=20)
        num_threads = min(20, len(observation_ids))
         
        # Initialize threads
        url_data = [[] for _ in observation_ids]
        for i in range(num_threads):
            worker = Thread(target=self.__previewWorker, args=(q, url_data))
            worker.setDaemon(True)
            worker.start()
            
        for i, obs_id in enumerate(observation_ids):
            q.put((obs_id, i))
        q.join()
        
        urls = jsonTools.mergeJson(url_data, 'url')
        
        return {'url' : urls}
    
    def __previewWorker(self, q, url_data):
        while True:
            obs_id, index = q.get()
            try:
                url_data[index] = self.preview(obs_id)
            except:
                sys.stderr.write(traceback.format_exc())
                sys.stderr.flush()
                thread.interrupt_main()
            q.task_done()
                            
    def downloadImages(self, urls, out_dir=None, return_image_data=False):
        return super(Observations, self).downloadImages(urls, out_dir=out_dir, return_image_data=return_image_data)










