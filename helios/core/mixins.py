"""Mixins and core functionality."""
import asyncio
import aiofiles
import aiohttp
import logging
import os
from collections import namedtuple
from io import BytesIO
from math import ceil

from PIL import Image

from helios import config
from helios.core.session import Session
from helios.core.structure import ImageRecord, Record
from helios.utilities import logging_utils, parsing_utils

logger = logging.getLogger(__name__)


class SDKCore(object):
    """
    Core class for Python interface to Helios Core APIs.

    This class must be inherited by any additional Core API classes.
    """
    _max_concurrency = config['max_concurrency']
    _verify_ssl = config['ssl_verify']

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

        # Create async semaphore for concurrency limit.
        self._async_semaphore = asyncio.Semaphore(value=self._max_concurrency)

        # Start session or use custom session.
        if session is None:
            self._session = Session()
        else:
            self._session = session

        # If the session hasn't been started, start it.
        if not self._session.token:
            self._session.start_session()

        self._auth_header = {
            self._session.token['name']: self._session.token['value']
        }

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

    @staticmethod
    def _get_all_items(queue):
        """
        Gets all items off an async queue.
        Args:
            queue (asyncio.Queue): Queue to get items from.
        Returns:
            list: Items from the queue.
        """

        items = []
        while True:
            try:
                items.append(queue.get_nowait())
            except asyncio.QueueEmpty:
                break
        return items


class IndexMixin(object):
    """Mixin for index queries."""

    @logging_utils.log_entrance_exit
    async def index(self, **kwargs):
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
        async with aiohttp.ClientSession(headers=self._auth_header) as session:
            initial_call = messages.pop(0)
            initial_query = self._index_query_builder(initial_call.kwargs,
                                                      initial_call.limit,
                                                      initial_call.skip)
            try:
                async with session.get(initial_query, raise_for_status=True) as resp:
                    initial_resp = Record(query=initial_query, content=await resp.json())
            except aiohttp.ClientError:
                logger.exception('First index query failed. Unable to continue.')
                raise

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
            return [initial_resp], []

        # Warn the user when truncation occurs. (max_skip is hit)
        if total > max_skip:
            logger.warning('Maximum skip level. Truncated results for: %s',
                           kwargs)

        # Get all results.
        success_queue = asyncio.Queue()
        failure_queue = asyncio.Queue()
        async with aiohttp.ClientSession(headers=self._auth_header) as session:
            tasks = []
            for msg in messages:
                tasks.append(
                    self._bound_index_worker(msg.kwargs, msg.limit, msg.skip,
                                             _session=session,
                                             _success_queue=success_queue,
                                             _failure_queue=failure_queue))
            await asyncio.gather(*tasks)

        succeeded = self._get_all_items(success_queue)
        failed = self._get_all_items(failure_queue)

        # Put initial query back in list.
        succeeded.insert(0, initial_resp)

        return succeeded, failed

    def _index_query_builder(self, index_kwargs, limit, skip):
        """
        Build index query string.

        Args:
            index_kwargs (dict): Any index query parameters.
            limit (int): Query limit.
            skip (int): Query skip.

        Returns:
            str: Query string.

        """

        params_str = self._parse_query_inputs(index_kwargs)

        query_str = '{}/{}?{}&limit={}&skip={}'.format(self._base_api_url,
                                                       self._core_api,
                                                       params_str,
                                                       limit,
                                                       skip)

        return query_str

    async def _bound_index_worker(self, *args, **kwargs):
        async with self._async_semaphore:
            return await self._index_worker(*args, **kwargs)

    async def _index_worker(self, index_kwargs, limit, skip, _session=None,
                            _success_queue=None, _failure_queue=None):
        """
        Handles index calls.

        Args:
            index_kwargs (dict): Any index query parameters.
            limit (int): Query limit.
            skip (int): Query skip.
            _session (aiohttp.ClientSession): Session instance.
            _success_queue (asyncio.Queue): Queue for successful calls.
            _failure_queue (asyncio.Queue): Queue for unsuccessful calls.

        """

        query_str = self._index_query_builder(index_kwargs, limit, skip)

        try:
            async with _session.get(query_str, raise_for_status=True) as resp:
                resp_json = await resp.json()
        except Exception as e:
            logger.exception('Failed to GET %s', query_str)
            await _failure_queue.put(Record(query=query_str, error=e))
            return

        await _success_queue.put(Record(query=query_str, content=resp_json))


class ShowMixin(object):
    """Mixin for show queries"""

    @logging_utils.log_entrance_exit
    async def show(self, ids):
        if not isinstance(ids, (list, tuple)):
            ids = [ids]

        tasks = []
        success_queue = asyncio.Queue()
        failure_queue = asyncio.Queue()
        async with aiohttp.ClientSession(headers=self._auth_header) as session:
            for id_ in ids:
                tasks.append(
                    self._bound_show_worker(id_,
                                            _session=session,
                                            _success_queue=success_queue,
                                            _failure_queue=failure_queue))
            await asyncio.gather(*tasks)

        succeeded = self._get_all_items(success_queue)
        failed = self._get_all_items(failure_queue)

        return succeeded, failed

    async def _bound_show_worker(self, *args, **kwargs):
        async with self._async_semaphore:
            return await self._show_worker(*args, **kwargs)

    async def _show_worker(self, id_, _session=None, _success_queue=None,
                           _failure_queue=None):
        """
        Handles show call.

        Args:
            id_ (str): Asset id.
            _session (aiohttp.ClientSession): Session instance.
            _success_queue (asyncio.Queue): Queue for successful calls.
            _failure_queue (asyncio.Queue): Queue for unsuccessful calls.

        """
        query_str = '{}/{}/{}'.format(self._base_api_url, self._core_api, id_)

        try:
            async with _session.get(query_str, raise_for_status=True) as resp:
                resp_json = await resp.json()
        except Exception as e:
            logger.exception('Failed to GET %s', query_str)
            await _failure_queue.put(Record(query=query_str, error=e))
            return

        await _success_queue.put(Record(query=query_str, content=resp_json))


class ShowImageMixin(object):
    """Mixin for show_image queries"""

    @logging_utils.log_entrance_exit
    async def show_image(self, id_, data, out_dir=None, return_image_data=False):
        if not isinstance(data, (list, tuple)):
            data = [data]

        # Make sure directory exists.
        if out_dir is not None:
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)

        tasks = []
        success_queue = asyncio.Queue()
        failure_queue = asyncio.Queue()
        async with aiohttp.ClientSession(headers=self._auth_header) as session:
            for x in data:
                tasks.append(
                    self._bound_show_image_worker(id_, x, out_dir=out_dir,
                                                  return_image_data=return_image_data,
                                                  _session=session,
                                                  _success_queue=success_queue,
                                                  _failure_queue=failure_queue))
            await asyncio.gather(*tasks)

        succeeded = self._get_all_items(success_queue)
        failed = self._get_all_items(failure_queue)

        return succeeded, failed

    async def _bound_show_image_worker(self, *args, **kwargs):
        async with self._async_semaphore:
            return await self._show_image_worker(*args, **kwargs)

    async def _show_image_worker(self, id_, data, out_dir=None, return_image_data=False,
                                 _session=None, _success_queue=None, _failure_queue=None):
        """
        Handles show_image call.

        Args:
            id_ (str): Asset id.
            data (list of str): Datapoints for the id. E.g. for cameras this is
                image times.
            out_dir (str, optional): Optionally write data to a directory.
            return_image_data (bool, optional): Optionally load image data
                into PIL and include in returned data.
            _session (aiohttp.ClientSession): Session instance.
            _success_queue (asyncio.Queue): Queue for successful calls.
            _failure_queue (asyncio.Queue): Queue for unsuccessful calls.

        """
        query_str = '{}/{}/{}/images/{}'.format(self._base_api_url,
                                                self._core_api,
                                                id_,
                                                data)

        try:
            async with _session.get(query_str, raise_for_status=True) as resp:
                image_content = await resp.read()
        except Exception as e:
            logger.exception('Failed to GET %s', query_str)
            await _failure_queue.put(ImageRecord(query=query_str, error=e))
            return

        # Parse key from url.
        parsed_url = parsing_utils.parse_url(str(resp.url))
        _, image_name = os.path.split(parsed_url.path)

        # Write image to file.
        if out_dir:
            out_file = os.path.join(out_dir, image_name)
            async with aiofiles.open(out_file, 'wb') as f:
                await f.write(image_content)
        else:
            out_file = None

        # Read and return image data.
        if return_image_data:
            # Read image from response.
            try:
                img_data = Image.open(BytesIO(image_content))
            except Exception as e:
                await _failure_queue.put(ImageRecord(query=query_str, error=e))
                return
        else:
            img_data = None

        await _success_queue.put(ImageRecord(query=query_str,
                                             name=image_name,
                                             content=img_data,
                                             output_file=out_file))
