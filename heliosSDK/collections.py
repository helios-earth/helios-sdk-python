'''
SDK for the Helios Collections API.  Methods are meant to represent the core
functionality in the developer documentation.  Some may have additional
functionality for convenience.  

@author: Michael A. Bayer
'''
import hashlib
from heliosSDK.core import SDKCore, IndexMixin, ShowMixin, ShowImageMixin, DownloadImagesMixin
from heliosSDK.utilities import jsonTools

from pathos.multiprocessing import freeze_support, ProcessingPool, cpu_count


class Collections(DownloadImagesMixin, ShowImageMixin, ShowMixin, IndexMixin, SDKCore):
    _CORE_API = 'collections'
    
    def __init__(self):
        self._startSession()
        
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
    
    def showImages(self, collection_id, camera=None, old_flag=False):
        results = self.images(collection_id, camera=camera, old_flag=old_flag)
        imgs = results['images']
        
        # Use hard-coded collections url.  Waiting for show image is too slow.
#         n_p = max([1, cpu_count()/2])
#         if n_p > 1 and len(imgs) > 4:
#             pool = ProcessingPool(n_p)
#             results2 = pool.map(self.showImage, [collection_id] * len(imgs), imgs)
#         else:
#             results2 = [self.showImage(collection_id, im) for im in imgs]
#         urls = jsonTools.mergeJson(results2, 'url')
        urls = ['https://helios-u-exelis.s3.amazonaws.com/collections/{}/{}'.format(collection_id, im) for im in imgs]

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
        
    def addImages(self, collection_id, img_list):
        results = [self.addImage(collection_id, im) for im in img_list]
        
        return results
    
    def removeImage(self, collection_id, img_url):
        query_str = '{}/{}/{}/images/{}'.format(self._BASE_API_URL,
                                                self._CORE_API,
                                                collection_id,
                                                img_url)
        resp = self._deleteRequest(query_str,
                                  headers={self._AUTH_TOKEN['name']:self._AUTH_TOKEN['value']},
                                  verify=self._SSL_VERIFY)
        
        json_response = resp.json()
        
        return json_response
        
    def removeImages(self, collection_id, img_list):
        results = [self.removeImage(collection_id, im) for im in img_list]
        
        return results   
    
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
        
        # show_images_class = ShowImage()
        results = self.showImages(collection_id)
        urls = results['url']
        
        # add_image_class = AddImage()
        results2 = self.addImages(new_id, urls)
        
        return results2
        
if __name__ == '__main__':
    freeze_support()        
        
        

        
        
