'''
SDK for the Helios Collections API.  Methods are meant to represent the core
functionality in the developer documentation.  Some may have additional
functionality for convenience.  

@author: Michael A. Bayer
'''
import hashlib
from heliosSDK.core import SDKCore, IndexMixin, ShowMixin, ShowImageMixin, DownloadImagesMixin
import sys
import traceback


# Python 2 and 3 fixes
try:
    import thread
except ImportError:
    import _thread as thread
    
    
class Collections(DownloadImagesMixin, ShowImageMixin, ShowMixin, IndexMixin, SDKCore):
    _CORE_API = 'collections'
    
    def __init__(self):
        pass
        
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
                
        resp = self._postRequest(urltmp,
                                headers=header,
                                data=parms,
                                verify=self._SSL_VERIFY)
        json_response = resp.json()
        
        return json_response
    
    def images(self, collection_id, camera=None, old_flag=False):
        max_limit = 200
        mark_img = ''    
        if camera is not None:
            md5_str = hashlib.md5(camera.encode('utf-8')).hexdigest()
            if not old_flag:
                camera = md5_str[0:4] + '-' + camera
            mark_img = camera
          
        good_images = []
        while True:
            results = self.show(collection_id, limit=max_limit, marker=mark_img)
            # Need most recent JSON results.
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
    
    def showImages(self, collection_id, image_names):
        # Use hard-coded collections url.  Waiting for show image is too slow.
        urls = ['https://helios-u-exelis.s3.amazonaws.com/collections/{}/{}'.format(collection_id, im) for im in image_names]

        return {'url':urls}
    
    def downloadImages(self, urls, out_dir=None, return_image_data=False):
        return super(Collections, self).downloadImages(urls, out_dir=out_dir, return_image_data=return_image_data) 

    def addImage(self, collection_id, img_url):
        # need to strip out the Bearer to work with a POST for collections
        post_token = self._AUTH_TOKEN['value'].replace('Bearer ', '') 
         
        parms = {'s3_src':img_url, 'access_token':post_token}
        header = {'name':'Content-Type', 'value':'application/x-www-form-urlencoded'}
        post_url = '{}/collections/{}/images'.format(self._BASE_API_URL, collection_id)
        resp = self._postRequest(post_url, headers=header, data=parms, verify=self._SSL_VERIFY)        
        json_response = resp.json()
        
        return json_response
        
    def addImages(self, collection_id, img_urls):
        # Set up the queue
        data = [[] for _ in img_urls]
        q = self._createQueue(self.__addImagesWorker,
                              data,
                              num_threads=min(20, len(img_urls)))
        
        # Process img_urls
        [q.put((x, collection_id, i)) for i, x in enumerate(img_urls)]          
        q.join()
                
        return data
    
    def __addImagesWorker(self, q, results):
        while True:
            img_url, coll_id, index = q.get()
            
            try:
                resp = self.addImage(coll_id, img_url)
                results[index] = resp
            except:
                sys.stderr.write(traceback.format_exc())
                sys.stderr.flush()  
                thread.interrupt_main()          
            q.task_done()
    
    def removeImage(self, collection_id, img_names):
        query_str = '{}/{}/{}/images/{}'.format(self._BASE_API_URL,
                                                self._CORE_API,
                                                collection_id,
                                                img_names)
        resp = self._deleteRequest(query_str,
                                  headers={self._AUTH_TOKEN['name']:self._AUTH_TOKEN['value']},
                                  verify=self._SSL_VERIFY)
        
        json_response = resp.json()
        
        return json_response
        
    def removeImages(self, collection_id, img_names):
        # Set up the queue
        data = [[] for _ in img_names]
        q = self._createQueue(self.__removeImagesWorker,
                              data,
                              num_threads=min(20, len(img_names)))
        
        # Process img_urls
        [q.put((x, collection_id, i)) for i, x in enumerate(img_names)]          
        q.join()
        
        return data   

    def __removeImagesWorker(self, q, results):
        while True:
            img, coll_id, index = q.get()
            
            try:
                resp = self.removeImage(coll_id, img)
                results[index] = resp
            except:
                sys.stderr.write(traceback.format_exc())
                sys.stderr.flush()  
                thread.interrupt_main()          
            q.task_done()                
            
    
    def copy(self, collection_id, new_collection_name):
     
        query_str = '{}/{}/{}'.format(self._BASE_API_URL,
                                      self._CORE_API,
                                      collection_id)
        resp = self._getRequest(query_str,
                               headers={self._AUTH_TOKEN['name']:self._AUTH_TOKEN['value']},
                               verify=self._SSL_VERIFY) 
        json_response = resp.json()
        
        output = self.create(new_collection_name, json_response['description'], json_response['tags'])
        new_id = output['collection_id']
        
        # Gather images that need to be copied.
        image_names = self.images(collection_id)
        results = self.showImages(collection_id, image_names['images'])
        urls = results['url']
        
        # add_image_class = AddImage()
        results2 = self.addImages(new_id, urls)
        
        return results2