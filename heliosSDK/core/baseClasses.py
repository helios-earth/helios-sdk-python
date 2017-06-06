'''
Core and Base objects for the heliosSDK. 

@author: Michael A. Bayer
'''
from Queue import Queue
from heliosSDK.core import RequestManager
from heliosSDK.session.tokenManager import TokenManager
from io import BytesIO
import json
import os
from threading import Thread
import warnings

import skimage.io


class SDKCore(RequestManager):
    """
    Core class for Python interface to Helios Core APIs.
    This class must be inherited by any additional Core API classes.
    """ 
    
    _BASE_API_URL = r'https://api.helios.earth/v1'
    _SSL_VERIFY = True
        
    def __init__(self):
        pass
        
    def _startSession(self):
        self._AUTH_TOKEN = TokenManager().startSession()      
             
    def _parseInputsForQuery(self, input_dict):
        query_str = ''
        for key in input_dict.keys():
            if isinstance(input_dict[key], (list, tuple)):
                query_str += str(key) + ','.join([str(x) for x in input_dict[key]]) + '&'
            else:
                query_str += str(key) + '=' + str(input_dict[key]) + '&'
        query_str = query_str[:-1]

        return query_str
    
    
class IndexMixin(object):
    _CORE_API = ''
    
    def __init__(self):
        pass
    
    def index(self, **kwargs):
        max_skip = 4000
        if 'limit' not in kwargs:
            limit = 100
        else:
            limit = kwargs.pop('limit')
            
        if 'skip' not in kwargs:
            skip = 0
        else:
            skip = kwargs.pop('skip')
        
        n = 0
        params_str = self._parseInputsForQuery(kwargs)
        temp_json = []
        while True:
            query_str = '{}/{}?{}&limit={}&skip={}'.format(self._BASE_API_URL,
                                                           self._CORE_API,
                                                           params_str,
                                                           limit,
                                                           skip)
            
            if skip > max_skip:
                warnings.warn('API warning for {}: The maximum skip value is {}. Truncated results were returned.'.format(query_str, max_skip), stacklevel=2)
                break
                
            resp = self._getRequest(query_str,
                            headers={self._AUTH_TOKEN['name']:self._AUTH_TOKEN['value']},
                            verify=self._SSL_VERIFY)
            
            geo_json_features = resp.json()
            
            # Collections API return 'results' rather than 'features'
            # and 'total' rather than 'properties'.'total'
            try:
                n += len(geo_json_features['features'])
            except:
                n += len(geo_json_features['results'])
            temp_json.append(geo_json_features)
            
            try:
                total_count = geo_json_features['properties']['total']
            except:
                total_count = geo_json_features['total']
                
            if n == total_count:
                break
            
            skip += limit
            
        return temp_json
            
class ShowMixin(object):
    _CORE_API = ''
    
    def __init__(self):
        pass
    
    def show(self, id_var, **kwargs):
        params_str = self._parseInputsForQuery(kwargs)
        query_str = '{}/{}/{}?{}'.format(self._BASE_API_URL,
                                      self._CORE_API,
                                      id_var,
                                      params_str)
        resp = self._getRequest(query_str,
                      headers={self._AUTH_TOKEN['name']:self._AUTH_TOKEN['value']},
                      verify=self._SSL_VERIFY) 
        geo_json_feature = resp.json()
        
        return geo_json_feature        
        
class ShowImageMixin(object):
    _CORE_API = ''
    
    def __init__(self):
        pass
    
    def showImage(self, id_var, x, **kwargs):
        params_str = self._parseInputsForQuery(kwargs)
        query_str = '{}/{}/{}/images/{}?{}'.format(self._BASE_API_URL,
                                                self._CORE_API,
                                                id_var,
                                                x,
                                                params_str) 
        resp = self._getRequest(query_str,
                               headers={self._AUTH_TOKEN['name']:self._AUTH_TOKEN['value']},
                               verify=self._SSL_VERIFY) 
        
        redirect_url = resp.url[0:resp.url.index('?')]
        
        resp2 = self._headRequest(redirect_url)
        
        # Check header for dud statuses. 
        if 'x-amz-meta-helios' in resp2.headers:
            hdrs = json.loads(resp2.headers['x-amz-meta-helios'])
            
            if hdrs['isOutcast'] or hdrs['isDud'] or hdrs['isFrozen']:
                warnings.warn('{} returned a dud image.'.format(redirect_url))
                return {'url' : None}

        return {'url' : redirect_url}
        
class DownloadImagesMixin(object):
    
    def __init__(self):
        pass
    
    def downloadImages(self, urls, out_dir=None, return_image_data=False):
        if not isinstance(urls, list):
            urls = [urls]
        
        if out_dir is not None:
            if not os.path.exists(out_dir):
                os.mkdir(out_dir)
                
        # Set up the queue
        q = Queue(maxsize=20)
        num_threads = min(20, len(urls))
         
        # Initialize threads
        image_data = [[] for x in urls]
        for i in range(num_threads):
            worker = Thread(target=self.__downloadRunner, args=(q, image_data))
            worker.setDaemon(True)
            worker.start()
            
        for i, url in enumerate(urls):
            q.put((url, out_dir, return_image_data, i))
        q.join()
            
        if return_image_data:
            return image_data
    
    def __downloadRunner(self, q, image_data):
        while True:
            url, out_dir, return_image_data, index = q.get()
            if url is not None:
                resp = self._getRequest(url)
                if out_dir is not None:
                    _, tail = os.path.split(url)
                    out_file = os.path.join(out_dir, tail)
                    with open(out_file, 'wb') as f:
                        for chunk in resp:
                            f.write(chunk)
                
                if return_image_data:
                    image_data[index] = skimage.io.imread(BytesIO(resp.content))
            q.task_done()