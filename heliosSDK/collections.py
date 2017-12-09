"""
SDK for the Helios Collections API.

Methods are meant to represent the core functionality in the developer
documentation.  Some may have additional functionality for convenience.

"""
import hashlib
import logging
from contextlib import closing
from itertools import repeat
from multiprocessing.dummy import Pool as ThreadPool

from heliosSDK.core import SDKCore, IndexMixin, ShowMixin, ShowImageMixin, \
    DownloadImagesMixin, RequestManager
from heliosSDK.utilities import logging_utils


class Collections(DownloadImagesMixin, ShowImageMixin, ShowMixin, IndexMixin, SDKCore):
    CORE_API = 'collections'
    MAX_THREADS = 32

    def __init__(self):
        self.request_manager = RequestManager(pool_maxsize=self.MAX_THREADS)
        self.logger = logging.getLogger(__name__)

    def index(self, **kwargs):
        return super(Collections, self).index(**kwargs)

    def show(self, collection_id, limit=200, marker=None):
        return super(Collections, self).show(collection_id,
                                             limit=limit,
                                             marker=marker)

    @logging_utils.log_entrance_exit
    def create(self, name, description, tags=None):
        # need to strip out the Bearer to work with a POST for collections
        post_token = self.request_manager._AUTH_TOKEN['value'].replace('Bearer ', '')

        # handle more than one tag
        if isinstance(tags, (list, tuple)):
            tags = ','.join(tags)

        # Compose parms block
        parms = {'name': name, 'description': description}
        if tags is not None:
            parms['tags'] = tags
        parms['access_token'] = post_token

        header = {'name': 'Content-Type',
                  'value': 'application/x-www-form-urlencoded'}

        post_url = '{}/{}'.format(self.BASE_API_URL, self.CORE_API)

        resp = self.request_manager.post(post_url, headers=header, data=parms)
        json_response = resp.json()

        return json_response

    @logging_utils.log_entrance_exit
    def update(self, collections_id, name=None, description=None, tags=None):
        if name is None and description is None and tags is None:
            raise ValueError('Update requires at least one named argument.')

        # need to strip out the Bearer to work with a PATCH for collections
        patch_token = self.request_manager._AUTH_TOKEN['value'].replace('Bearer ', '')

        # handle more than one tag
        if isinstance(tags, (list, tuple)):
            tags = ','.join(tags)

        # Compose parms block
        parms = {}
        if name is not None:
            parms['name'] = name
        if description is not None:
            parms['description'] = description
        if tags is not None:
            parms['tags'] = tags
        parms['access_token'] = patch_token

        header = {'name': 'Content-Type',
                  'value': 'application/x-www-form-urlencoded'}

        patch_url = '{}/{}/{}'.format(self.BASE_API_URL,
                                      self.CORE_API,
                                      collections_id)

        resp = self.request_manager.patch(patch_url,
                                          headers=header,
                                          data=parms)
        json_response = resp.json()

        return json_response

    @logging_utils.log_entrance_exit
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
            results = self.show(collection_id,
                                limit=max_limit,
                                marker=mark_img)

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

        return json_output

    def show_image(self, collection_id, image_names, check_for_duds=False):
        return super(Collections, self).show_image(
            collection_id, image_names, check_for_duds=check_for_duds)

    def download_images(self, urls, out_dir=None, return_image_data=False):
        return super(Collections, self).download_images(
            urls, out_dir=out_dir, return_image_data=return_image_data)

    @logging_utils.log_entrance_exit
    def add_image(self, collection_id, urls):
        # Force iterable
        if not isinstance(urls, (list, tuple)):
            urls = [urls]
        n_urls = len(urls)

        # Get number of threads
        num_threads = min(self.MAX_THREADS, n_urls)

        # Process urls.
        if num_threads > 1:
            with closing(ThreadPool(num_threads)) as thread_pool:
                data = thread_pool.map(self.__add_image_worker,
                                       zip(repeat(collection_id), urls))
        else:
            data = [self.__add_image_worker((collection_id, urls[0]))]

        # Remove errors, if they exist
        data = [x for x in data if x != -1]

        # Determine how many were successful
        n_data = len(data)
        message = 'addImage({} out of {} successful)'.format(n_data, n_urls)

        if n_data == 0:
            self.logger.error(message)
            return -1
        elif n_data < n_urls:
            self.logger.warning(message)
        else:
            self.logger.info(message)

        return data

    def __add_image_worker(self, args):
        coll_id, img_url = args

        # need to strip out the Bearer to work with a POST for collections
        post_token = self.request_manager._AUTH_TOKEN['value'].replace('Bearer ', '')

        # Compose post request
        parms = {'s3_src': img_url, 'access_token': post_token}
        header = {'name': 'Content-Type',
                  'value': 'application/x-www-form-urlencoded'}
        post_url = '{}/collections/{}/images'.format(self.BASE_API_URL,
                                                     coll_id)

        try:
            resp = self.request_manager.post(post_url,
                                             headers=header,
                                             data=parms)
        except Exception:
            return -1

        return resp.json()

    @logging_utils.log_entrance_exit
    def remove_image(self, collection_id, names):
        # Force iterable
        if not isinstance(names, (list, tuple)):
            names = [names]
        n_names = len(names)

        # Get number of threads
        num_threads = min(self.MAX_THREADS, n_names)

        # Process urls.
        if num_threads > 1:
            with closing(ThreadPool(num_threads)) as thread_pool:
                data = thread_pool.map(self.__remove_image_worker,
                                       zip(repeat(collection_id), names))
        else:
            data = [self.__remove_image_worker((collection_id, names[0]))]

        # Remove errors, if they exist
        data = [x for x in data if x != -1]

        # Determine how many were successful
        n_data = len(data)
        message = 'removeImage({} out of {} successful)'.format(n_data, n_names)

        if n_data == 0:
            self.logger.error(message)
            return -1
        elif n_data < n_names:
            self.logger.warning(message)
        else:
            self.logger.info(message)

        return data

    def __remove_image_worker(self, args):
        coll_id, img_name = args

        query_str = '{}/{}/{}/images/{}'.format(self.BASE_API_URL,
                                                self.CORE_API,
                                                coll_id,
                                                img_name)

        try:
            resp = self.request_manager.delete(query_str)
        except Exception:
            return -1

        return resp.json()

    @logging_utils.log_entrance_exit
    def copy(self, collection_id, new_name):
        query_str = '{}/{}/{}'.format(self.BASE_API_URL,
                                      self.CORE_API,
                                      collection_id)

        resp = self.request_manager.get(query_str)
        json_response = resp.json()

        output = self.create(new_name,
                             json_response['description'],
                             json_response['tags'])

        new_id = output['collection_id']

        # Gather images that need to be copied.
        image_names = self.images(collection_id)
        results = self.show_image(collection_id, image_names['images'])
        urls = results['url']

        # Add images to new collection.
        results2 = self.add_image(new_id, urls)

        return results2
