"""Mixins and core functionality."""
import json
import os
from collections import namedtuple
from contextlib import closing
from io import BytesIO
from math import ceil
from multiprocessing.pool import ThreadPool

import numpy as np
import requests
from PIL import Image
from helios.core.request_manager import RequestManager
from helios.core.session import Session
from helios.utilities import logging_utils, parsing_utils


class SDKCore(object):
    """
    Core class for Python interface to Helios Core APIs.

    This class must be inherited by any additional Core API classes.
    """
    _max_threads = 32

    def __init__(self, session=None):
        """
        Initialize core API instance.

        If a session has been started prior to initialization it can be used
        via the session input parameter. If this is not used a session will
        be started automatically.

        Args:
            session (helios.Session object, optional): An instance of the
                Session. Defaults to None. If unused a session will be
                created for you.

        """
        # Start session or use custom session.
        if session is None:
            self._session = Session()
        else:
            self._session = session

        # If the session hasn't been started, start it.
        if not self._session.token:
            self._session.start_session()

        # Create request manager to handle all API requests.
        self._request_manager = RequestManager(self._session.token,
                                               pool_maxsize=self._max_threads)

    @staticmethod
    def _parse_query_inputs(input_dict):
        # Check for unique case: sensors
        if 'sensors' in input_dict:
            query_str = input_dict.pop('sensors') + '&'
        else:
            query_str = ''

        # Parse input_dict into a str
        for key, val in input_dict.items():
            if val is None:
                continue

            if isinstance(val, (list, tuple)):
                query_str += (str(key) +
                              '=' +
                              ','.join([str(x) for x in val]) +
                              '&')
            else:
                query_str += (str(key) + '=' + str(val) + '&')

        # Remove final ampersand
        query_str = query_str[:-1]

        return query_str

    @staticmethod
    def _check_headers_for_dud(header_data):
        if 'x-amz-meta-helios' in header_data:
            meta_block = json.loads(header_data['x-amz-meta-helios'])
            if meta_block['isOutcast'] or meta_block['isDud'] or meta_block['isFrozen']:
                return True
        return False

    @property
    def _base_api_url(self):
        return self._session.api_url

    @_base_api_url.setter
    def _base_api_url(self, value):
        raise AttributeError('Access to _base_api_url is restricted.')

    def _process_messages(self, func, messages):
        # Create thread pool
        with closing(ThreadPool(self._max_threads)) as thread_pool:
            results = thread_pool.map(func, messages)
        return results


class IndexMixin(object):
    @logging_utils.log_entrance_exit
    def index(self, **kwargs):
        max_skip = 4000
        limit = kwargs.get('limit', 100)
        skip = kwargs.get('skip', 0)

        # Establish all queries.
        params_str = self._parse_query_inputs(kwargs)
        queries = []
        for i in range(skip, max_skip, limit):
            if i + limit > max_skip:
                temp_limit = max_skip - i
            else:
                temp_limit = limit

            query_str = '{}/{}?{}&limit={}&skip={}'.format(self._base_api_url,
                                                           self._core_api,
                                                           params_str,
                                                           temp_limit,
                                                           i)

            queries.append(query_str)

        # Do first query to find total number of results to expect.
        initial_resp = self._request_manager.get(queries.pop(0)).json()

        try:
            total = initial_resp['properties']['total']
        except KeyError:
            total = initial_resp['total']

        # Warn the user when truncation occurs. (max_skip is hit)
        if total > max_skip:
            # Log truncation warning
            self._logger.warning('Maximum skip level. Truncated results for: %s',
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
        self._logger.info('%s index queries required for: %s', n_queries_needed, kwargs)

        # Create messages for worker.
        Message = namedtuple('Message', 'query')
        messages = [Message(x) for x in queries]

        # Process messages using the worker function.
        results = self._process_messages(self.__index_worker, messages)

        # Put initial query back in list.
        results.insert(0, initial_resp)

        return results

    def __index_worker(self, msg):
        """msg must contain query"""
        # Perform query
        resp = self._request_manager.get(msg.query)

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
            sequence of dicts: GeoJSON feature results.

        """
        if not isinstance(ids, (list, tuple)):
            ids = [ids]

        # Create messages for worker.
        Message = namedtuple('Message', 'id_')
        messages = [Message(x) for x in ids]

        # Process messages using the worker function.
        results = self._process_messages(self.__show_worker, messages)

        return results

    def __show_worker(self, msg):
        """msg must contain id_"""
        query_str = '{}/{}/{}'.format(self._base_api_url, self._core_api, msg.id_)
        resp = self._request_manager.get(query_str)

        return resp.json()


class ShowImageMixin(object):
    @logging_utils.log_entrance_exit
    def show_image(self, id_, data, out_dir=None, return_image_data=False):
        if not isinstance(data, (list, tuple)):
            data = [data]

        # Create messages for worker.
        Message = namedtuple('Message', ['id_', 'data', 'out_dir', 'return_image_data'])
        messages = [Message(id_, x, out_dir, return_image_data) for x in data]

        # Process messages using the worker function.
        results = self._process_messages(self.__show_image_worker, messages)

        # Remove errors, if they exist
        results = [x for x in results if x != -1]

        # Determine how many were successful
        n_data = len(results)
        n_samples = len(data)
        message = 'showImage({} out of {} successful)'.format(n_data, n_samples)

        if n_data == 0:
            self._logger.error(message)
            return -1
        elif n_data < n_samples:
            self._logger.warning(message)
        else:
            self._logger.info(message)

        return results

    def __show_image_worker(self, msg):
        """msg must contain id_, data, out_dir, and return_image_data"""
        query_str = '{}/{}/{}/images/{}'.format(self._base_api_url,
                                                self._core_api,
                                                msg.id_,
                                                msg.data)

        try:
            resp = self._request_manager.get(query_str)
        except requests.exceptions.RequestException as e:
            return ShowImageRecord(query=query_str, error=e)

        # Parse key from url.
        parsed_url = parsing_utils.parse_url(resp.url)
        _, asset_key = os.path.split(parsed_url.path)

        # Read image from response.
        img = Image.open(BytesIO(resp.content))

        # Write image to file.
        if msg.out_dir is not None:
            out_file = os.path.join(msg.out_dir, asset_key)
            img.save(out_file)
        else:
            out_file = None

        # Read and return image data.
        if msg.return_image_data:
            img_data = np.array(img)
        else:
            img_data = None

        return ShowImageRecord(query=query_str, key=asset_key, data=img_data,
                               output_file=out_file)


class ShowImageRecord(object):
    def __init__(self, query=None, key=None, data=None, output_file=None, error=None):
        self.query = query
        self.key = key
        self.data = data
        self.output_file = output_file
        self.error = error

    @property
    def ok(self):
        if self.error:
            return False
        else:
            return True
