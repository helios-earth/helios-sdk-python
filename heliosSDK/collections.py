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
        
        urltmp = '{}/{}'.format(self._BASE_API_URL,
                                self._CORE_API)
        
        # Log
        self.logger.info('Creating collection: {}'.format(name))
                
        resp = self._postRequest(urltmp,
                                headers=header,
                                data=parms,
                                verify=self._SSL_VERIFY)
        json_response = resp.json()
        
        # Log success
        self.logger.info('Successfully created collection: {}'.format(name))
        
        return json_response
    
    def images(self, collection_id, camera=None, old_flag=False):
        max_limit = 200
        mark_img = ''    
        if camera is not None:
            md5_str = hashlib.md5(camera.encode('utf-8')).hexdigest()
            if not old_flag:
                camera = md5_str[0:4] + '-' + camera
            mark_img = camera
            
        # Log start of query
        self.logger.info('Starting images query: {},{}'.format(collection_id, camera))
        
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
        
        return json_output
    
    def showImage(self, collection_id, image_name):
        return super(Collections, self).showImage(collection_id, image_name)
    
    def downloadImages(self, urls, out_dir=None, return_image_data=False):
        return super(Collections, self).downloadImages(urls, out_dir=out_dir, 
                                                       return_image_data=return_image_data) 

    def addImage(self, collection_id, url_data):
        if isinstance(url_data, str):
            url_data = [url_data]
        
        # Log start
        self.logger.info('Starting addImage queries for {} images in {}.'.format(len(url_data)), collection_id)
        
        # Check number of threads
        num_threads = min(self.MAX_THREADS, len(url_data))
        
        # Process urls.
        if num_threads > 4:
            POOL = ThreadPool(num_threads)
            data = POOL.map(self.__addImagesWorker,
                            zip(repeat(collection_id), url_data))
        else:
            data = map(self.__addImagesWorker,
                       zip(repeat(collection_id), url_data))
        
        # Log success
        self.logger.info('addImage queries complete. {} out of {} successful.'.format(len([x for x in data if x is not None]), len(url_data)))
        
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
    
    def removeImage(self, collection_id, name_data):
        if isinstance(name_data, str):
            name_data = [name_data]
            
        # Log start
        self.logger.info('Starting removeImage queries for {} images in {}.'.format(len(name_data)), collection_id)

        # Check number of threads
        num_threads = min(self.MAX_THREADS, len(name_data))
        
        # Process urls.
        if num_threads > 4:
            POOL = ThreadPool(num_threads)
            data = POOL.map(self.__addImagesWorker,
                            zip(repeat(collection_id), name_data))
        else:
            data = map(self.__removeImagesWorker,
                       zip(repeat(collection_id), name_data))
            
        # Log success
        self.logger.info('removeImage queries complete. {} out of {} successful.'.format(len([x for x in data if x is not None]), len(name_data)))            
        
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
            self.logger.error('Error {}: {}, {}'.format(resp.status_code, coll_id, img_name))
            return None
        
        # Log query
        self.logger.info('Query complete: {}'.format(query_str))        
                
        return resp.json()
    
    def copy(self, collection_id, new_collection_name):
        query_str = '{}/{}/{}'.format(self._BASE_API_URL,
                                      self._CORE_API,
                                      collection_id)
        
        # Log start
        self.logger.info('Starting copy query for {} with new name {}'.format(collection_id, new_collection_name))
        
        resp = self._getRequest(query_str,
                               headers={self._AUTH_TOKEN['name']:self._AUTH_TOKEN['value']},
                               verify=self._SSL_VERIFY) 
        json_response = resp.json()
        
        output = self.create(new_collection_name, json_response['description'], json_response['tags'])
        new_id = output['collection_id']
        
        # Gather images that need to be copied.
        image_names = self.images(collection_id)
        results = self.showImage(collection_id, image_names['images'])
        urls = results['url']
        
        # Add images to new collection.
        results2 = self.addImage(new_id, urls)
        
        # Log success
        self.logger.info('Copying complete.'.format(new_id))
        
        return results2
