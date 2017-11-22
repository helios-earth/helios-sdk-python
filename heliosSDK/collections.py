'''
SDK for the Helios Collections API.  Methods are meant to represent the core
functionality in the developer documentation.  Some may have additional
functionality for convenience.  

@author: Michael A. Bayer
'''
import hashlib
import logging
from itertools import repeat
from multiprocessing.dummy import Pool as ThreadPool

from heliosSDK.core import SDKCore, IndexMixin, ShowMixin, ShowImageMixin, DownloadImagesMixin, RequestManager


class Collections(DownloadImagesMixin, ShowImageMixin, ShowMixin, IndexMixin, SDKCore):
    CORE_API = 'collections'
    MAX_THREADS = 32

    def __init__(self):
        self.requestManager = RequestManager(pool_maxsize=self.MAX_THREADS)
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

        parms = {'name': name,
                 'description': description,
                 'tags': tags,
                 'access_token': post_token}
        header = {'name': 'Content-Type',
                  'value': 'application/x-www-form-urlencoded'}

        post_url = '{}/{}'.format(self.BASE_API_URL, self.CORE_API)

        resp = self.requestManager.post(post_url, headers=header, data=parms)
        json_response = resp.json()

        # Log success
        self.logger.info('Leaving create(new_id={})'.format(json_response['collection_id']))

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
                imgs_found_temp = [x for x in images_found if x.split('_')[0] == camera]
            else:
                imgs_found_temp = images_found

            if not imgs_found_temp:
                break

            good_images.extend(imgs_found_temp)
            if len(imgs_found_temp) < len(images_found):
                break
            else:
                mark_img = good_images[-1]

        json_output = {'total': len(good_images),
                       'images': good_images}

        # Log success
        self.logger.info('Leaving images({} images found)'.format(len(good_images)))

        return json_output

    def showImage(self, collection_id, image_names):
        return super(Collections, self).showImage(collection_id, image_names)

    def downloadImages(self, urls, out_dir=None, return_image_data=False):
        return super(Collections, self).downloadImages(urls, out_dir=out_dir,
                                                       return_image_data=return_image_data)

    def addImage(self, collection_id, urls):
        # Force iterable
        if not isinstance(urls, (list, tuple)):
            urls = [urls]
        n_urls = len(urls)

        # Log start
        self.logger.info('Entering addImage(collection_id={}, N={})'.format(collection_id, n_urls))

        # Get number of threads
        num_threads = min(self.MAX_THREADS, n_urls)

        # Process urls.
        if num_threads > 1:
            with ThreadPool(num_threads) as POOL:
                data = POOL.map(self.__addImagesWorker,
                                zip(repeat(collection_id), urls))
        else:
            data = [self.__addImagesWorker((collection_id, urls[0]))]

        # Remove errors, if they exist
        data = [x for x in data if x != -1]

        # Check results for errors
        n_data = len(data)
        message = 'Leaving addImage({} out of {} successful)'.format(n_data, n_urls)
        if n_data == 0:
            self.logger.error(message)
            return -1
        elif n_data < n_urls:
            self.logger.warning(message)
        else:
            self.logger.info(message)

        return data

    def __addImagesWorker(self, args):
        coll_id, img_url = args

        # need to strip out the Bearer to work with a POST for collections
        post_token = self._AUTH_TOKEN['value'].replace('Bearer ', '')

        # Compose post request
        parms = {'s3_src': img_url, 'access_token': post_token}
        header = {'name': 'Content-Type', 'value': 'application/x-www-form-urlencoded'}
        post_url = '{}/collections/{}/images'.format(self.BASE_API_URL, coll_id)

        try:
            resp = self.requestManager.post(post_url, headers=header, data=parms)
        except Exception:
            return -1

        return resp.json()

    def removeImage(self, collection_id, names):
        # Force iterable
        if not isinstance(names, (list, tuple)):
            names = [names]
        n_names = len(names)

        # Log start
        self.logger.info('Entering removeImage(collection_id={}, N={})'.format(collection_id, n_names))

        # Get number of threads
        num_threads = min(self.MAX_THREADS, n_names)

        # Process urls.
        if num_threads > 1:
            with ThreadPool(num_threads) as POOL:
                data = POOL.map(self.__removeImagesWorker,
                                zip(repeat(collection_id), names))
        else:
            data = [self.__removeImagesWorker((collection_id, names[0]))]

        # Remove errors, if they exist
        data = [x for x in data if x != -1]

        # Check results for errors
        n_data = len(data)
        message = 'Leaving removeImage({} out of {} successful)'.format(n_data, n_names)
        if n_data == 0:
            self.logger.error(message)
            return -1
        elif n_data < n_names:
            self.logger.warning(message)
        else:
            self.logger.info(message)

        return data

    def __removeImagesWorker(self, args):
        coll_id, img_name = args

        query_str = '{}/{}/{}/images/{}'.format(self.BASE_API_URL,
                                                self.CORE_API,
                                                coll_id,
                                                img_name)

        try:
            resp = self.requestManager.delete(query_str)
        except Exception:
            return -1

        return resp.json()

    def copy(self, collection_id, new_name):
        # Log start
        self.logger.info('Entering copy(collection_id={}, new_name={}'.format(collection_id, new_name))

        query_str = '{}/{}/{}'.format(self.BASE_API_URL,
                                      self.CORE_API,
                                      collection_id)

        resp = self.requestManager.get(query_str)
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
