"""Mixins and core functionality."""
import logging
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
from helios.core.structure import ImageRecord, Record
from helios.utilities import logging_utils, parsing_utils

logger = logging.getLogger(__name__)


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

    @property
    def _base_api_url(self):
        return self._session.api_url

    @_base_api_url.setter
    def _base_api_url(self, value):
        raise AttributeError('Access to _base_api_url is restricted.')

    @staticmethod
    def _parse_query_inputs(parameters):
        """
        Create query string from a dictionary of parameters.

        Args:
            parameters (dict):  Key/values to combine into a query string.

        Returns:
            str: Query string.
        """
        parameters_temp = parameters.copy()

        query_str = ''

        # Check for unique case: sensors
        if 'sensors' in parameters_temp:
            query_str += parameters_temp.pop('sensors') + '&'

        # Parse input_dict into a str
        for key, val in parameters_temp.items():
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

    def _process_messages(self, func, messages):
        n_messages = len(messages)
        logger.info('%s processing %s messages.', func.__name__, n_messages)

        # Create thread pool
        with closing(ThreadPool(min(self._max_threads, n_messages))) as thread_pool:
            results = thread_pool.map(func, messages)

        try:
            n_successful = sum([True for x in results if x.ok])
        except AttributeError:
            pass
        else:
            log_message = '{} out of {} successful'.format(n_successful, n_messages)
            if n_successful == 0:
                logger.error(log_message)
            elif n_successful < n_messages:
                logger.warning(log_message)
            else:
                logger.info(log_message)

        return results


class IndexMixin(object):
    """Mixin for index queries."""

    @logging_utils.log_entrance_exit
    def index(self, **kwargs):
        max_skip = 4000

        limit = int(kwargs.pop('limit', 100))
        skip = int(kwargs.pop('skip', 0))

        # Raise right away if skip is too high.
        if skip > max_skip:
            raise ValueError('skip must be less than the maximum skip value '
                             'of {}. A value of {} was tried.'.format(max_skip, skip))

        # Create the messages up to the maximum skip.
        Message = namedtuple('Message', ['kwargs', 'limit', 'skip'])

        messages = []
        for i in range(skip, max_skip, limit):
            if i + limit > max_skip:
                temp_limit = max_skip - i
            else:
                temp_limit = limit
            messages.append(Message(kwargs=kwargs, limit=temp_limit, skip=i))

        # Process first message.
        initial_resp = self.__index_worker(messages.pop(0))

        # Handle first query failing.
        if not initial_resp.ok:
            logger.error('First query failed. Unable to continue.')
            raise initial_resp.error

        # Get total number of features available.
        try:
            total = initial_resp.content['properties']['total']
        except KeyError:
            total = initial_resp.content['total']

        # Determine number of iterations that will be needed.
        n_queries_needed = int(ceil((total - skip) / float(limit)))
        messages = messages[0:n_queries_needed - 1]

        # Log number of queries required.
        logger.info('%s index queries required for: %s', n_queries_needed, kwargs)

        # If only one query was necessary, return immediately.
        if total <= limit:
            return [initial_resp]

        # Warn the user when truncation occurs. (max_skip is hit)
        if total > max_skip:
            logger.warning('Maximum skip level. Truncated results for: %s',
                           kwargs)

        # Process messages using the worker function.
        results = self._process_messages(self.__index_worker, messages)

        # Put initial query back in list.
        results.insert(0, initial_resp)

        return results

    def __index_worker(self, msg):
        """msg must contain kwargs (search criteria), limit, and skip"""

        params_str = self._parse_query_inputs(msg.kwargs)

        query_str = '{}/{}?{}&limit={}&skip={}'.format(self._base_api_url,
                                                       self._core_api,
                                                       params_str,
                                                       msg.limit,
                                                       msg.skip)

        # Perform query
        try:
            resp = self._request_manager.get(query_str)
        except requests.exceptions.RequestException as e:
            return Record(message=msg, query=query_str, error=e)

        return Record(message=msg, query=query_str, content=resp.json())


class ShowMixin(object):
    """Mixin for show queries"""

    @logging_utils.log_entrance_exit
    def show(self, ids):
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

        try:
            resp = self._request_manager.get(query_str)
        except requests.exceptions.RequestException as e:
            return Record(message=msg, query=query_str, error=e)

        return Record(message=msg, query=query_str, content=resp.json())


class ShowImageMixin(object):
    """Mixin for show_image queries"""

    @logging_utils.log_entrance_exit
    def show_image(self, id_, data, out_dir=None, return_image_data=False):
        if not isinstance(data, (list, tuple)):
            data = [data]

        # Create messages for worker.
        Message = namedtuple('Message', ['id_', 'data', 'out_dir', 'return_image_data'])
        messages = [Message(id_, x, out_dir, return_image_data) for x in data]

        # Make sure directory exists.
        if out_dir:
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)

        # Process messages using the worker function.
        results = self._process_messages(self.__show_image_worker, messages)

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
            return ImageRecord(message=msg, query=query_str, error=e)

        # Parse key from url.
        parsed_url = parsing_utils.parse_url(resp.url)
        _, image_name = os.path.split(parsed_url.path)

        # Write image to file.
        if msg.out_dir is not None:
            out_file = os.path.join(msg.out_dir, image_name)
            with open(out_file, 'wb') as f:
                f.write(resp.content)
        else:
            out_file = None

        # Read and return image data.
        if msg.return_image_data:
            # Read image from response.
            img_data = np.asarray(Image.open(BytesIO(resp.content)))
        else:
            img_data = None

        return ImageRecord(message=msg, query=query_str, name=image_name,
                           content=img_data, output_file=out_file)
