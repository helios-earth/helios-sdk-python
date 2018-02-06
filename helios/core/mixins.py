"""Mixins and core functionality."""
import json
import os
from contextlib import closing
from io import BytesIO
from itertools import repeat
from math import ceil
from multiprocessing.pool import ThreadPool

import numpy as np
from PIL import Image

from helios.core.request_manager import RequestManager
from helios.core.session import Session
from helios.utilities import logging_utils


class SDKCore(object):
    """
    Core class for Python interface to Helios Core APIs.

    This class must be inherited by any additional Core API classes.
    """
    max_threads = 32

    def __init__(self, session=None):
        """
        Initialize core capabilities.

        If a session has been started prior to initialization it can be used
        via the session input parameter. If this is not used a session will
        be started automatically.

        Args:
            session (Session object, optional): An instance of the
                Session. Defaults to None. If unused a session will be
                created for you.

        """
        # Start session or use custom session.
        if session is None:
            self.session = Session()
        else:
            self.session = session

        # If the session hasn't been started, start it.
        if not self.session.token:
            self.session.start_session()

        # Create request manager to handle all API requests.
        self.request_manager = RequestManager(self.session.token,
                                              pool_maxsize=self.max_threads)

    @staticmethod
    def parse_query_inputs(input_dict):
        # Check for unique case: sensors
        if 'sensors' in input_dict.keys():
            query_str = input_dict.pop('sensors') + '&'
        else:
            query_str = ''

        # Parse input_dict into a str
        for key in input_dict.keys():
            if isinstance(input_dict[key], (list, tuple)):
                query_str += (str(key) +
                              '=' +
                              ','.join([str(x) for x in input_dict[key]]) +
                              '&')
            else:
                query_str += (str(key) + '=' + str(input_dict[key]) + '&')
        query_str = query_str[:-1]

        return query_str

    @staticmethod
    def check_headers_for_dud(header_data):
        if 'x-amz-meta-helios' in header_data:
            meta_block = json.loads(header_data['x-amz-meta-helios'])
            if meta_block['isOutcast'] or meta_block['isDud'] or meta_block['isFrozen']:
                return True
        return False

    @property
    def base_api_url(self):
        return self.session.api_url

    @base_api_url.setter
    def base_api_url(self, value):
        raise AttributeError('Access to base_api_url is restricted.')


class IndexMixin(object):
    @logging_utils.log_entrance_exit
    def index(self, **kwargs):
        max_skip = 4000
        limit = kwargs.get('limit', 100)
        skip = kwargs.get('skip', 0)

        # Establish all queries.
        params_str = self.parse_query_inputs(kwargs)
        queries = []
        for i in range(skip, max_skip, limit):
            if i + limit > max_skip:
                temp_limit = max_skip - i
            else:
                temp_limit = limit

            query_str = '{}/{}?{}&limit={}&skip={}'.format(self.base_api_url,
                                                           self.core_api,
                                                           params_str,
                                                           temp_limit,
                                                           i)

            queries.append(query_str)

        # Do first query to find total number of results to expect.
        initial_resp = self.request_manager.get(queries.pop(0)).json()

        try:
            total = initial_resp['properties']['total']
        except KeyError:
            total = initial_resp['total']

        # Warn the user when truncation occurs. (max_skip is hit)
        if total > max_skip:
            # Log truncation warning
            self.logger.warning('Maximum skip level. Truncated results for: %s',
                                kwargs)

        # Get number of results in initial query.
        try:
            n_features = len(initial_resp['features'])
        except KeyError:
            n_features = len(initial_resp['results'])

        # If only one query was necessary, return immediately.
        if n_features < limit:
            return [initial_resp]

        # Determine number of iterations that will be needed.
        n_queries_needed = int(ceil((total - skip) / float(limit))) - 1
        queries = queries[0:n_queries_needed]

        # Log number of queries required.
        self.logger.info('%s index queries required for: %s', n_queries_needed,
                         kwargs)

        # Create thread pool and get results
        num_threads = min(self.max_threads, n_queries_needed)
        if num_threads > 1:
            with closing(ThreadPool(num_threads)) as thread_pool:
                results = thread_pool.map(self.__index_worker, queries)
        else:
            results = [self.__index_worker(queries[0])]

        # Put initial query back in list.
        results.insert(0, initial_resp)

        return results

    def __index_worker(self, args):
        query_str = args

        # Perform query
        resp = self.request_manager.get(query_str)

        return resp.json()


class ShowMixin(object):
    @logging_utils.log_entrance_exit
    def show(self, ids):
        """
        Return attributes for Helios assets.

        For example, the input ids can be a single Alert ID, or a list of
        Alert IDs.  Can also be camera or observation IDs.

        Args:
            ids (str or sequence of strs): Helios asset ID(s). This can
                include an alert, observation, or camera ID.

        Returns:
            (sequence of dicts): GeoJSON feature results.

        """
        # Force iterable
        if not isinstance(ids, (list, tuple)):
            ids = [ids]
        n_ids = len(ids)

        # Get number of threads
        num_threads = min(self.max_threads, n_ids)

        if num_threads > 1:
            with closing(ThreadPool(num_threads)) as thread_pool:
                results = thread_pool.map(self.__show_worker, ids)
        else:
            results = [self.__show_worker(ids[0])]

        return results

    def __show_worker(self, args):
        id_ = args

        query_str = '{}/{}/{}'.format(self.base_api_url, self.core_api, id_)

        resp = self.request_manager.get(query_str)

        return resp.json()


class ShowImageMixin(object):
    @logging_utils.log_entrance_exit
    def show_image(self, id_, samples, check_for_duds=True):
        # Force iterable
        if not isinstance(samples, (list, tuple)):
            samples = [samples]
        n_samples = len(samples)

        # Get number of threads
        num_threads = min(self.max_threads, n_samples)

        # Process urls.
        if num_threads > 1:
            with closing(ThreadPool(num_threads)) as thread_pool:
                results = thread_pool.map(self.__show_image_worker,
                                          zip(repeat(id_),
                                              samples,
                                              repeat(check_for_duds)))
        else:
            results = [self.__show_image_worker((id_, samples[0],
                                                 check_for_duds))]

        # Remove errors, if they exist
        results = [x for x in results if x != -1]

        # Determine how many were successful
        n_data = len(results)
        message = 'showImage({} out of {} successful)'.format(n_data, n_samples)

        if n_data == 0:
            self.logger.error(message)
            return -1
        elif n_data < n_samples:
            self.logger.warning(message)
        else:
            self.logger.info(message)

        return results

    def __show_image_worker(self, args):
        id_, data, check_for_duds = args

        query_str = '{}/{}/{}/images/{}'.format(self.base_api_url,
                                                self.core_api,
                                                id_,
                                                data)

        try:
            resp = self.request_manager.get(query_str)
            redirect_url = resp.url[0:resp.url.index('?')]
        except Exception:
            return -1

        # Check header for dud statuses.
        if check_for_duds:
            try:
                # Redirect URLs do not use api credentials
                resp2 = self.request_manager.head(redirect_url,
                                                  use_api_cred=False)
            except Exception:
                return -1

            if self.check_headers_for_dud(resp2.headers):
                self.logger.info('showImage query returned dud image: %s',
                                 query_str)
                return None

        return redirect_url


class DownloadImagesMixin(object):
    @logging_utils.log_entrance_exit
    def download_images(self, urls, out_dir=None, return_image_data=False):
        """Download images from URLs.

        Args:
            urls (str or sequence of strs): Image URLs to download from.
            out_dir (str, optional): Output directory to save images to.
                Defaults to None.
            return_image_data (bool, optional): If True, image data will be
                read into a Numpy ndarray and returned. Defaults to False.

        Returns:
            sequence of ndarrays or None: Image data if return_image_data is
            True or None otherwise.

        """
        # Force iterable
        if not isinstance(urls, (list, tuple)):
            urls = [urls]
        n_urls = len(urls)

        if out_dir is not None:
            if not os.path.exists(out_dir):
                os.mkdir(out_dir)

        # Create thread pool
        num_threads = min(self.max_threads, n_urls)
        if num_threads > 1:
            with closing(ThreadPool(num_threads)) as thread_pool:
                data = thread_pool.map(self.__download_images_worker,
                                       zip(urls, repeat(out_dir),
                                           repeat(return_image_data)))
        else:
            data = [self.__download_images_worker((urls[0],
                                                   out_dir,
                                                   return_image_data))]

        # Remove errors, if the exist
        data = [x for x in data if isinstance(x, np.ndarray) or x != -1]

        # Determine how many were successful
        n_data = len(data)
        message = 'downloadImages({} out of {} successful)'.format(n_data, n_urls)

        if n_data == 0:
            self.logger.error(message)
            return -1
        elif n_data < n_urls:
            self.logger.warning(message)
        else:
            self.logger.info(message)

        if return_image_data:
            return data

    def __download_images_worker(self, args):
        url, out_dir, return_image_data = args

        try:
            resp = self.request_manager.get(url, use_api_cred=False)
        except Exception:
            return -1

        # Read image from response
        img = Image.open(BytesIO(resp.content))

        # Write image to file.
        if out_dir is not None:
            _, tail = os.path.split(url)
            out_file = os.path.join(out_dir, tail)
            img.save(out_file)

        # Read and return image data.
        if return_image_data:
            return np.array(img)
