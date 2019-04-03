"""
Mixins and core functionality.

Note: Mixins, in this case, simply refers to shared code.

"""
import functools
import logging
import os
from queue import Queue, Empty
from io import BytesIO
from multiprocessing.pool import ThreadPool

import requests
from PIL import Image
from requests import adapters

from helios.core.structure import ImageRecord, Record
from helios.utilities import logging_utils, parsing_utils

logger = logging.getLogger(__name__)


class SDKCore:
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

        # Check for sessions that have not been started.
        if session.auth_header is None:
            raise ValueError(
                'No authorization header was found in the session. '
                'Make sure the session has been started.'
            )

    @property
    def _base_api_url(self):
        return self._session.api_url

    @property
    def _auth_header(self):
        return self._session.auth_header

    @property
    def _max_threads(self):
        return self._session.max_threads

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
        Gets all items off a queue.

        Args:
            queue (queue.Queue): Queue to get items from.

        Returns:
            list: Items from the queue.

        """

        items = []
        while True:
            try:
                items.append(queue.get_nowait())
            except Empty:
                break
        return items

    def _batch_process(self, func, iterable, **kwargs):
        """
        Batch process each element in an iterable with a worker function.

        This assumes the input argument to iterate over is in the first
        position.

        The worker function must also follow the design of all other workers
        in the SDK. I.e. they must accept _success_queue, _failure_queue, and
        _session as private input parameters.

        Args:
            func (function): Worker function reference.
            iterable (list): List of data to be processed by the func.
            **kwargs: Any function input arguments to pre-fill using
                partial.  These parameters will be used for each item in the
                iterable. E.g. f(iterable, a, b, c=5) ->
                _batch_process(worker_func, iterable, a=val1, b=val2)

        Returns:
            tuple: A tuple containing the successful and failed API call
                records.

        """

        n_tasks = len(iterable)

        logger.info('Processing %s calls to %s.', n_tasks, func.__name__)

        if '_success_queue' in kwargs:
            success_queue = kwargs['_success_queue']
        else:
            success_queue = Queue()
            kwargs['_success_queue'] = success_queue

        if '_failure_queue' in kwargs:
            failure_queue = kwargs['_failure_queue']
        else:
            failure_queue = Queue()
            kwargs['_failure_queue'] = failure_queue

        n_threads = min(self._max_threads, n_tasks)

        def _do_work(func, iterable):
            """Helper function to do work in batch or direct call if single task."""
            if len(iterable) > 1:
                with ThreadPool(n_threads) as pool:
                    pool.map(func, iterable)
            else:
                func(iterable[0])

        if '_session' in kwargs:
            worker = functools.partial(func, **kwargs)
            _do_work(worker, iterable)
        else:
            with requests.Session() as session:
                session.headers.update(self._auth_header)
                session.mount(
                    'https://',
                    adapters.HTTPAdapter(pool_maxsize=n_threads, max_retries=2),
                )
                kwargs['_session'] = session
                worker = functools.partial(func, **kwargs)
                _do_work(worker, iterable)

        succeeded = self._get_all_items(success_queue)
        failed = self._get_all_items(failure_queue)

        _n_succeeded = len(succeeded)
        _n_failed = len(failed)
        _log_message = f'{_n_succeeded} out of {n_tasks} successful'
        if _n_succeeded == 0:
            logger.error(_log_message)
        elif _n_succeeded < n_tasks:
            logger.warning(_log_message)
        else:
            logger.info(_log_message)

        return succeeded, failed


class IndexMixin:
    """Mixin for index queries."""

    @logging_utils.log_entrance_exit
    def index(self, **kwargs):
        max_limit = 100
        max_skip = 4000

        starting_skip = int(kwargs.pop('skip', 0))
        if 'limit' not in kwargs:
            kwargs['limit'] = max_limit

        # Raise right away if skip is too high.
        if starting_skip > max_skip:
            raise ValueError(
                'skip must be less than the maximum skip value '
                'of {}. A value of {} was tried.'.format(max_skip, starting_skip)
            )

        initial_succeeded, initial_failed = self._batch_process(
            self._index_worker, [starting_skip], query_params=kwargs
        )
        if initial_failed:
            raise initial_failed[0].error
        else:
            initial_call = initial_succeeded[0]

        # Get total number of features available.
        try:
            total = initial_call.content['properties']['total']
        except KeyError:
            total = initial_call.content['total']

        # If only one query was necessary, return immediately.
        if total <= kwargs['limit']:
            return [initial_call], []

        # Warn the user when truncation will occur. (max_skip is hit)
        if total > max_skip:
            logger.warning('Maximum skip level. Truncated results for: %s', kwargs)

        skips = [
            skip
            for skip in range(starting_skip + kwargs['limit'], total, kwargs['limit'])
        ]

        succeeded, failed = self._batch_process(
            self._index_worker, skips, query_params=kwargs
        )

        # Put initial query back in list.
        succeeded.insert(0, initial_call)

        return succeeded, failed

    def _index_query_builder(self, **kwargs):
        """
        Build index query string.

        Args:
            kwargs: Any index query parameters.

        Returns:
            str: Query string.

        """

        params_str = self._parse_query_inputs(**kwargs)

        query_str = '{}/{}?{}'.format(self._base_api_url, self._core_api, params_str)

        return query_str

    def _index_worker(
        self,
        skip,
        query_params,
        _session=None,
        _success_queue=None,
        _failure_queue=None,
    ):
        """
        Handles index calls.

        Args:
            skip (int): Query skip.
            query_params (dict): Any optional search parameters.
            _session (requests.Session): Session instance.
            _success_queue (queue.Queue): Queue for successful calls.
            _failure_queue (queue.Queue): Queue for unsuccessful calls.

        """
        call_params = locals()
        query_str = self._index_query_builder(skip=skip, **query_params)

        try:
            resp = _session.get(query_str, verify=self._ssl_verify)
            resp.raise_for_status()
        except Exception as e:
            logger.exception('Failed to GET %s', query_str)
            _failure_queue.put(Record(url=query_str, parameters=call_params, error=e))
            return

        resp_json = resp.json()

        _success_queue.put(
            Record(url=query_str, parameters=call_params, content=resp_json)
        )


class ShowMixin:
    """Mixin for show queries"""

    @logging_utils.log_entrance_exit
    def show(self, ids):
        if not isinstance(ids, (list, tuple)):
            ids = [ids]

        succeeded, failed = self._batch_process(self._show_worker, ids)

        return succeeded, failed

    def _show_worker(
        self, asset_id, _session=None, _success_queue=None, _failure_queue=None
    ):
        """
        Handles show call.

        Args:
            asset_id (str): Asset id.
            _session (requests.Session): Session instance.
            _success_queue (queue.Queue): Queue for successful calls.
            _failure_queue (queue.Queue): Queue for unsuccessful calls.

        """

        call_params = locals()

        query_str = '{}/{}/{}'.format(self._base_api_url, self._core_api, asset_id)

        try:
            resp = _session.get(query_str, verify=self._ssl_verify)
            resp.raise_for_status()
        except Exception as e:
            logger.exception('Failed to GET %s', query_str)
            _failure_queue.put(Record(url=query_str, parameters=call_params, error=e))
            return

        resp_json = resp.json()

        _success_queue.put(
            Record(url=query_str, parameters=call_params, content=resp_json)
        )


class ShowImageMixin:
    """Mixin for show_image queries"""

    @logging_utils.log_entrance_exit
    def show_image(self, data, asset_id, out_dir=None, return_image_data=False):
        if not isinstance(data, (list, tuple)):
            data = [data]

        # Make sure directory exists.
        if out_dir is not None:
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)

        succeeded, failed = self._batch_process(
            self._show_image_worker,
            data,
            asset_id=asset_id,
            out_dir=out_dir,
            return_image_data=return_image_data,
        )

        return succeeded, failed

    def _show_image_worker(
        self,
        data,
        asset_id,
        out_dir=None,
        return_image_data=False,
        _session=None,
        _success_queue=None,
        _failure_queue=None,
    ):
        """
        Handles show_image call.

        Args:
            data (list of str): Datapoints for the id. E.g. for cameras this is
                image times.
            asset_id (str): Asset id.
            out_dir (str, optional): Optionally write data to a directory.
            return_image_data (bool, optional): Optionally load image data
                into PIL and include in returned data.
            _session (requests.Session): Session instance.
            _success_queue (queue.Queue): Queue for successful calls.
            _failure_queue (queue.Queue): Queue for unsuccessful calls.

        """

        call_params = locals()

        query_str = '{}/{}/{}/images/{}'.format(
            self._base_api_url, self._core_api, asset_id, data
        )

        try:
            resp = _session.get(query_str, verify=self._ssl_verify)
            resp.raise_for_status()
        except Exception as e:
            logger.exception('Failed to GET %s', query_str)
            _failure_queue.put(
                ImageRecord(url=query_str, parameters=call_params, error=e)
            )
            return

        image_content = resp.content

        # Parse key from url.
        parsed_url = parsing_utils.parse_url(str(resp.url))
        _, image_name = os.path.split(parsed_url.path)

        # Write image to file.
        if out_dir:
            out_file = os.path.join(out_dir, image_name)
            with open(out_file, 'wb') as f:
                f.write(image_content)
        else:
            out_file = None

        # Read and return image data.
        if return_image_data:
            # Read image from response.
            try:
                img_data = Image.open(BytesIO(image_content))
            except Exception as e:
                _failure_queue.put(
                    ImageRecord(url=query_str, parameters=call_params, error=e)
                )
                return
        else:
            img_data = None

        _success_queue.put(
            ImageRecord(
                url=query_str,
                parameters=call_params,
                name=image_name,
                content=img_data,
                filename=out_file,
            )
        )
