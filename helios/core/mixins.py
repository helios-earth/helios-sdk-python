"""Mixins and core functionality."""
import asyncio
import functools
import logging
import os
from io import BytesIO

import aiofiles
import aiohttp
from PIL import Image

from helios.core.structure import ImageRecord, Record
from helios.utilities import logging_utils, parsing_utils

logger = logging.getLogger(__name__)


class SDKCore(object):
    """
    Core class for Python interface to Helios Core APIs.

    This class must be inherited by any additional Core API classes.
    """

    def __init__(self, session):
        """
        Initialize core API instance.

        If a session has been started prior to initialization it can be used
        via the session input parameter. If this is not used a session will
        be started automatically.

        Args:
            session (helios.HeliosSession): An instance of the
                Session. Defaults to None. If unused a session will be
                created for you.

        """

        self._session = session

    @property
    def _base_api_url(self):
        return self._session.api_url

    @property
    def _auth_header(self):
        return self._session.auth_header

    @property
    def _async_semaphore(self):
        return self._session.async_semaphore

    @property
    def _ssl_verify(self):
        return self._session.ssl_verify

    @staticmethod
    def _parse_query_inputs(**kwargs):
        """
        Create query string from a dictionary of parameters.

        Args:
            kwargs:  Key/values to combine into a query string.

        Returns:
            str: Query string.
        """
        parameters_temp = kwargs.copy()

        query_str = ''

        # Check for unique case: sensors
        if 'sensors' in parameters_temp:
            query_str += parameters_temp.pop('sensors') + '&'

        # Parse input_dict into a str
        for key, val in parameters_temp.items():
            if val is None:
                continue

            if isinstance(val, (list, tuple)):
                query_str += str(key) + '=' + ','.join([str(x) for x in val]) + '&'
            elif isinstance(val, bool):
                query_str += str(key) + '=' + str(val).lower() + '&'
            else:
                query_str += str(key) + '=' + str(val) + '&'

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
        starting_skip = int(kwargs.pop('skip', 0))

        # Raise right away if skip is too high.
        if starting_skip > max_skip:
            raise ValueError(
                'skip must be less than the maximum skip value '
                'of {}. A value of {} was tried.'.format(max_skip, starting_skip)
            )

        # Get all results.
        success_queue = asyncio.Queue()
        failure_queue = asyncio.Queue()
        async with aiohttp.ClientSession(headers=self._auth_header) as session:
            worker = functools.partial(
                self._bound_index_worker,
                _session=session,
                _success_queue=success_queue,
                _failure_queue=failure_queue
            )

            await worker(limit, starting_skip, **kwargs)
            try:
                initial_call = success_queue.get_nowait()
            except asyncio.QueueEmpty:
                failure = failure_queue.get_nowait()
                raise failure.error

            # Get total number of features available.
            try:
                total = initial_call.content['properties']['total']
            except KeyError:
                total = initial_call.content['total']

            # If only one query was necessary, return immediately.
            if total <= limit:
                return [initial_call], []

            # Warn the user when truncation will occur. (max_skip is hit)
            if total > max_skip:
                logger.warning('Maximum skip level. Truncated results for: %s', kwargs)

            tasks = [worker(limit, skip, **kwargs) for skip in
                     range(starting_skip + limit, total, limit)]
            logger.info('%s index queries required for: %s', len(tasks) + 1, kwargs)
            await asyncio.gather(*tasks)

        succeeded = self._get_all_items(success_queue)
        failed = self._get_all_items(failure_queue)

        # Put initial query back in list.
        succeeded.insert(0, initial_call)

        return succeeded, failed

    def _index_query_builder(self, limit, skip, **kwargs):
        """
        Build index query string.

        Args:
            limit (int): Query limit.
            skip (int): Query skip.
            kwargs: Any index query parameters.

        Returns:
            str: Query string.

        """

        params_str = self._parse_query_inputs(**kwargs)

        query_str = '{}/{}?{}&limit={}&skip={}'.format(
            self._base_api_url, self._core_api, params_str, limit, skip
        )

        return query_str

    async def _bound_index_worker(self, *args, **kwargs):
        async with self._async_semaphore:
            return await self._index_worker(*args, **kwargs)

    async def _index_worker(
        self,
        limit,
        skip,
        _session=None,
        _success_queue=None,
        _failure_queue=None,
        **kwargs
    ):
        """
        Handles index calls.

        Args:
            limit (int): Query limit.
            skip (int): Query skip.
            _session (aiohttp.ClientSession): Session instance.
            _success_queue (asyncio.Queue): Queue for successful calls.
            _failure_queue (asyncio.Queue): Queue for unsuccessful calls.
            kwargs (dict): Any index query parameters.

        """

        query_str = self._index_query_builder(limit, skip, **kwargs)

        try:
            async with _session.get(
                query_str, raise_for_status=True, ssl=self._ssl_verify
            ) as resp:
                resp_json = await resp.json()
        except Exception as e:
            logger.exception('Failed to GET %s', query_str)
            await _failure_queue.put(Record(url=query_str, error=e))
            return

        await _success_queue.put(Record(url=query_str, content=resp_json))


class ShowMixin(object):
    """Mixin for show queries"""

    @logging_utils.log_entrance_exit
    async def show(self, ids):
        if not isinstance(ids, (list, tuple)):
            ids = [ids]

        success_queue = asyncio.Queue()
        failure_queue = asyncio.Queue()
        async with aiohttp.ClientSession(headers=self._auth_header) as session:
            worker = functools.partial(
                self._bound_show_worker,
                _session=session,
                _success_queue=success_queue,
                _failure_queue=failure_queue
            )
            tasks = [worker(id_) for id_ in ids]
            await asyncio.gather(*tasks)

        succeeded = self._get_all_items(success_queue)
        failed = self._get_all_items(failure_queue)

        return succeeded, failed

    async def _bound_show_worker(self, *args, **kwargs):
        async with self._async_semaphore:
            return await self._show_worker(*args, **kwargs)

    async def _show_worker(
        self, id_, _session=None, _success_queue=None, _failure_queue=None
    ):
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
            async with _session.get(
                query_str, raise_for_status=True, ssl=self._ssl_verify
            ) as resp:
                resp_json = await resp.json()
        except Exception as e:
            logger.exception('Failed to GET %s', query_str)
            await _failure_queue.put(Record(url=query_str, error=e))
            return

        await _success_queue.put(Record(url=query_str, content=resp_json))


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

        success_queue = asyncio.Queue()
        failure_queue = asyncio.Queue()
        async with aiohttp.ClientSession(headers=self._auth_header) as session:
            worker = functools.partial(
                self._bound_show_image_worker,
                out_dir=out_dir,
                return_image_data=return_image_data,
                _session=session,
                _success_queue=success_queue,
                _failure_queue=failure_queue
            )
            tasks = [worker(id_, x) for x in data]
            await asyncio.gather(*tasks)

        succeeded = self._get_all_items(success_queue)
        failed = self._get_all_items(failure_queue)

        return succeeded, failed

    async def _bound_show_image_worker(self, *args, **kwargs):
        async with self._async_semaphore:
            return await self._show_image_worker(*args, **kwargs)

    async def _show_image_worker(
        self,
        id_,
        data,
        out_dir=None,
        return_image_data=False,
        _session=None,
        _success_queue=None,
        _failure_queue=None,
    ):
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
        query_str = '{}/{}/{}/images/{}'.format(
            self._base_api_url, self._core_api, id_, data
        )

        try:
            async with _session.get(
                query_str, raise_for_status=True, ssl=self._ssl_verify
            ) as resp:
                image_content = await resp.read()
        except Exception as e:
            logger.exception('Failed to GET %s', query_str)
            await _failure_queue.put(ImageRecord(url=query_str, error=e))
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
                await _failure_queue.put(ImageRecord(url=query_str, error=e))
                return
        else:
            img_data = None

        await _success_queue.put(
            ImageRecord(
                url=query_str, name=image_name, content=img_data, output_file=out_file
            )
        )
