'''
SDK for the Helios Collections API.  Methods are meant to represent the core
functionality in the developer documentation.  Some may have additional
functionality for convenience.  

@author: Michael A. Bayer
'''
import hashlib
from heliosSDK.core import SDKCore, IndexMixin, ShowMixin, ShowImageMixin, DownloadImagesMixin
from itertools import repeat
import logging
from multiprocessing.dummy import Pool as ThreadPool    


class Collections(DownloadImagesMixin, ShowImageMixin, ShowMixin, IndexMixin, SDKCore):
    MAX_THREADS = 20
    
    _CORE_API = 'collections'
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def index(self, **kwargs):
        return super(Collections, self).index(**kwargs)
    
    def show(self, collection_id, limit=200, marker=None):
        return super(Collections, self).show(collection_id, limit=limit, marker=marker)
    
    def create(self, name, description, tags=None):
        if tags is None:
            tags = ''
            
        # Log start
        self.logger.info('Entering create(name={}, description={}, tags={}'.format(name, description, tags))            

        # need to strip out the Bearer to work with a POST for collections
        post_token = self._AUTH_TOKEN['value'].replace('Bearer ', '')
        
        # handle more than one tag
        if isinstance(tags, (list, tuple)):
            tags = ','.join(tags)
        
        parms = {'name':name,
                 'description':description,
                 'tags':tags,
                 'access_token':post_token}
        header = {'name':'Content-Type',
                  'value':'application/x-www-form-urlencoded'}
        
        post_url = '{}/{}'.format(self._BASE_API_URL,
                                  self._CORE_API)
                
        resp = self._postRequest(post_url,
                                headers=header,
                                data=parms,
                                verify=self._SSL_VERIFY)
        
        # Log errors
        if not resp.ok:
            self.logger.error('Error {}: {}'.format(resp.status_code, post_url))
            return None
        
        json_response = resp.json()
        
        # Log success
        self.logger.info('Leaving create()'.format(json_response['collection_id']))
        
        return json_response
    
    def images(self, collection_id, camera=None, old_flag=False):
        max_limit = 200
        mark_img = ''
        
        # Log start
        self.logger.info('Entering images(collection_id={}, camera={})'.format(collection_id, camera))
        
        if camera is not None:
            md5_str = hashlib.md5(camera.encode('utf-8')).hexdigest()
            if not old_flag:
                camera = md5_str[0:4] + '-' + camera
            mark_img = camera
        
        good_images = []
        while True:
            results = self.show(collection_id, limit=max_limit, marker=mark_img)
            
            # Gather images.
            images_found = results['images']
            
            if camera is not None:
                imgs_found_temp = list(filter(lambda x: x.split('_')[0] == camera, images_found))
            else:
                imgs_found_temp = images_found
                
            if not imgs_found_temp:
                break
                
            good_images.extend(imgs_found_temp)
            if len(imgs_found_temp) < len(images_found):
                break
            else:
                mark_img = good_images[-1]
        
        json_output = {'total':len(good_images),
                       'images':good_images}
        
        # Log success
        self.logger.info('Leaving images({} images found)'.format(len(good_images)))
        
        return json_output
    
    def showImage(self, collection_id, image_names):
        return super(Collections, self).showImage(collection_id, image_names)
    
    def downloadImages(self, urls, out_dir=None, return_image_data=False):
        return super(Collections, self).downloadImages(urls, out_dir=out_dir, 
                                                       return_image_data=return_image_data) 

    def addImage(self, collection_id, urls):        
        # Force list
        if isinstance(urls, str):
            urls = [urls]
            
        # Log start
        self.logger.info('Entering addImage(collection_id={}, N={})'.format(collection_id, len(urls)))            
        
        # Get number of threads
        num_threads = min(self.MAX_THREADS, len(urls))
        
        # Process urls.
        if num_threads > 4:
            POOL = ThreadPool(num_threads)
            data = POOL.map(self.__addImagesWorker,
                            zip(repeat(collection_id), urls))
        else:
            data = map(self.__addImagesWorker,
                       zip(repeat(collection_id), urls))
            
        # Remove errors, if they exist
        data = [x for x in data if x is not None]
        
        # Log success
        self.logger.info('Leaving addImage({} out of {} successful)'.format(len(data), len(urls)))
        
        return data
    
    def __addImagesWorker(self, args):
        coll_id, img_url = args
        
        # need to strip out the Bearer to work with a POST for collections
        post_token = self._AUTH_TOKEN['value'].replace('Bearer ', '') 
        
        # Compose post request
        parms = {'s3_src':img_url, 'access_token':post_token}
        header = {'name':'Content-Type', 'value':'application/x-www-form-urlencoded'}
        post_url = '{}/collections/{}/images'.format(self._BASE_API_URL, coll_id)
        
        # Log query
        self.logger.info('Query began: {}'.format(post_url))
        
        resp = self._postRequest(post_url, headers=header, data=parms, verify=self._SSL_VERIFY)   
        
        # Log errors
        if not resp.ok:
            self.logger.error('Error {}: {}, {}'.format(resp.status_code, coll_id, img_url))
            return None
        
        # Log success
        self.logger.info('Query complete: {}'.format(post_url))
        
        return resp.json()
    
    def removeImage(self, collection_id, names):
        # Force list
        if isinstance(names, str):
            names = [names]

        # Log start
        self.logger.info('Entering removeImage(collection_id={}, N={})'.format(collection_id, len(names)))

        # Get number of threads
        num_threads = min(self.MAX_THREADS, len(names))
        
        # Process urls.
        if num_threads > 4:
            POOL = ThreadPool(num_threads)
            data = POOL.map(self.__addImagesWorker,
                            zip(repeat(collection_id), names))
        else:
            data = map(self.__removeImagesWorker,
                       zip(repeat(collection_id), names))
            
        # Remove errors, if they exist
        data = [x for x in data if x is not None]
            
        # Log success
        self.logger.info('Leaving removeImage({} out of {} successful)'.format(len(data), len(names)))            
        
        return data

    def __removeImagesWorker(self, args):
        coll_id, img_name = args
        
        query_str = '{}/{}/{}/images/{}'.format(self._BASE_API_URL,
                                                self._CORE_API,
                                                coll_id,
                                                img_name)
        
        # Log query
        self.logger.info('Query begin: {}'.format(query_str))        
        
        resp = self._deleteRequest(query_str,
                                  headers={self._AUTH_TOKEN['name']:self._AUTH_TOKEN['value']},
                                  verify=self._SSL_VERIFY)
        
        # Log errors
        if not resp.ok:
            self.logger.error('Error {}: {}'.format(resp.status_code, query_str))
            return None
        
        # Log query
        self.logger.info('Query complete: {}'.format(query_str))        
                
        return resp.json()
    
    def copy(self, collection_id, new_name):
        # Log start
        self.logger.info('Entering copy(collection_id={}, new_name={}'.format(collection_id, new_name))
        
        query_str = '{}/{}/{}'.format(self._BASE_API_URL,
                                      self._CORE_API,
                                      collection_id)
        
        resp = self._getRequest(query_str,
                               headers={self._AUTH_TOKEN['name']:self._AUTH_TOKEN['value']},
                               verify=self._SSL_VERIFY) 
        json_response = resp.json()
        
        output = self.create(new_name, json_response['description'], json_response['tags'])
        new_id = output['collection_id']
        
        # Gather images that need to be copied.
        image_names = self.images(collection_id)
        results = self.showImage(collection_id, image_names['images'])
        urls = results['url']
        
        # Add images to new collection.
        results2 = self.addImage(new_id, urls)
        
        # Log success
        self.logger.info('Leaving copy(new_id={})'.format(new_id))
        
        return results2
