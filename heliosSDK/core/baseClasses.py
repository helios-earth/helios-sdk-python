'''
Core and Base objects for the heliosSDK. 

@author: Michael A. Bayer
'''
from heliosSDK import AUTH_TOKEN, BASE_API_URL
from heliosSDK.core import RequestManager
from io import BytesIO
from itertools import repeat
import json
from math import ceil
from multiprocessing.dummy import Pool as ThreadPool
import os
import sys

import scipy.misc


class SDKCore(RequestManager):
    """
    Core class for Python interface to Helios Core APIs.
    This class must be inherited by any additional Core API classes.
    """ 
    
    _BASE_API_URL = BASE_API_URL
    _SSL_VERIFY = True
    _AUTH_TOKEN = AUTH_TOKEN 
             
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
    
    def index(self, **kwargs):
        max_skip = 4000
        limit = kwargs.get('limit', 100)
        skip = kwargs.get('skip', 0)
            
        # Establish all queries.
        params_str = self._parseInputsForQuery(kwargs)
        queries = []
        for i in range(skip, max_skip, limit):
            if i + limit > max_skip: 
                temp_limit = max_skip - i
            else:
                temp_limit = limit
                
            query_str = '{}/{}?{}&limit={}&skip={}'.format(self._BASE_API_URL,
                                                           self._CORE_API,
                                                           params_str,
                                                           temp_limit,
                                                           i)
            
            queries.append(query_str)
            
        
        # Do first query to find total number of results to expect.
        initial_resp = self._getRequest(queries.pop(0),
                                        headers={self._AUTH_TOKEN['name']:self._AUTH_TOKEN['value']},
                                        verify=self._SSL_VERIFY)
            
        initial_resp_json = initial_resp.json()
        try:
            total = initial_resp_json['properties']['total']
        except:
            total = initial_resp_json['total']
            
        # Warn the user when truncation occurs. (max_skip is hit)
        if total > max_skip:
            sys.stderr.write('Maximum skip level reached for this query.  Truncated results will be returned.' + os.linesep)
            sys.stderr.flush()
            
        # Get number of results in initial query.
        try:
            n = len(initial_resp_json['features'])
        except:
            n = len(initial_resp_json['results'])
            
        # If only one query was necessary, return immediately.
        if n < limit:
            return [initial_resp_json]
        
        # Determine number of iterations that will be needed.
        n_queries_needed = int(ceil((total - skip) / float(limit))) - 1
        queries = queries[0:n_queries_needed]
        
        # Create thread pool
        num_threads = min(self.MAX_THREADS, n_queries_needed)
        POOL = ThreadPool(num_threads)
        
        results = POOL.map(self.__indexWorker, queries)
              
        # Put initial query back in list.
        results.insert(0, initial_resp_json)
        
        return results
    
    def __indexWorker(self, args):
        query_str = args
        resp = self._getRequest(query_str,
                                headers={self._AUTH_TOKEN['name']:self._AUTH_TOKEN['value']},
                                verify=self._SSL_VERIFY)
        return resp.json()
            
class ShowMixin(object):
    
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
                sys.stderr.write('{} returned a dud image.'.format(redirect_url) + os.linesep)
                sys.stderr.flush()
                return {'url' : None}

        return {'url' : redirect_url}
        
class DownloadImagesMixin(object):
        
    def downloadImages(self, urls, out_dir=None, return_image_data=False):
        if not isinstance(urls, list):
            raise TypeError('urls should be a list of URL strings.')
        
        if out_dir is not None:
            if not os.path.exists(out_dir):
                os.mkdir(out_dir)
        
        # Create thread pool
        num_threads = min(self.MAX_THREADS, len(urls))
        POOL = ThreadPool(num_threads)
        
        image_data = POOL.map(self.__downloadWorker,
                              zip(urls, repeat(out_dir), repeat(return_image_data)))
            
        if return_image_data:
            return image_data
    
    def __downloadWorker(self, args):
        url, out_dir, return_image_data = args

        if url is not None:
            resp = self._getRequest(url)
            if out_dir is not None:
                _, tail = os.path.split(url)
                out_file = os.path.join(out_dir, tail)
                with open(out_file, 'wb') as f:
                    for chunk in resp:
                        f.write(chunk)                
            if return_image_data:
                return scipy.misc.imread(BytesIO(resp.content))