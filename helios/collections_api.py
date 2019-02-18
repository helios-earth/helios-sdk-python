"""
Helios Collections API.

Methods are meant to represent the core functionality in the developer
documentation.  Some may have additional functionality for convenience.

"""
import asyncio
import functools
import hashlib
import logging

import aiohttp

from helios.core.mixins import SDKCore, IndexMixin, ShowImageMixin
from helios.core.structure import Record
from helios.utilities import logging_utils

logger = logging.getLogger(__name__)


class Collections(ShowImageMixin, IndexMixin, SDKCore):
    """
    The Collections API allows users to group and organize individual image
    frames.

    Collections are intended to be short-lived resources and will be accessible
    for 90 days from the time the collection was created. After that time
    period has expired, the collection and all associated imagery will be
    removed from the system.

    """

    _core_api = 'collections'

    def __init__(self, session):
        """
        Initialize Collection instance.

        Args:
            session (helios.HeliosSession): An instance of the
                Session. Defaults to None. If unused a session will be
                created for you.

        """
        super().__init__(session)

    @logging_utils.log_entrance_exit
    async def add_image(self, assets, collection_id):
        """
        Add images to a collection from Helios assets.

        `assets` dictionary templates:

        .. code-block:: python3

            # Asset examples that can be included in the `assets` input list.
            data = {'camera_id': ''}
            data = {'camera_id': '', 'time': ''}
            data = {'observation_id': ''}
            data = {'collection_id': '', 'image': ''}

        Usage example:

        .. code-block:: python3

            import helios
            async with helios.HeliosSession() as sess:
                coll_inst = helios.Collections(sess)
                camera_id = '...'
                times = [...] # List of image times.
                destination_id = '...'
                data = [{'camera_id': camera_id, 'time': x} for x in times]
                results, failures = await coll_inst.add_image(data, destination_id)

        Args:
            assets (dict or list of dicts): Data containing any of these
                payloads (camera_id), (camera_id, time), (observation_id),
                (collection_id, image). E.g. data =
                [{'camera_id': 'cam_01', time: '2017-01-01T00:00:000Z'}]
            collection_id (str): Collection ID.

        Returns:
            tuple: A tuple containing:
                succeeded (list of :class:`Record <helios.core.structure.Record>`):
                    Successful API call records.
                failed (list of :class:`Record <helios.core.structure.Record>`):
                    Failed API call records.

        """

        assert isinstance(assets, (list, tuple, dict))

        if isinstance(assets, dict):
            assets = [assets]

        success_queue = asyncio.Queue()
        failure_queue = asyncio.Queue()
        async with aiohttp.ClientSession(headers=self._auth_header) as session:
            worker = functools.partial(
                self._bound_add_image_worker,
                collection_id,
                _session=session,
                _success_queue=success_queue,
                _failure_queue=failure_queue,
            )
            tasks = [worker(data) for data in assets]
            await asyncio.gather(*tasks)

        succeeded = self._get_all_items(success_queue)
        failed = self._get_all_items(failure_queue)

        return succeeded, failed

    async def _bound_add_image_worker(self, *args, **kwargs):
        async with self._async_semaphore:
            return await self._add_image_worker(*args, **kwargs)

    async def _add_image_worker(
        self,
        collection_id,
        data,
        _session=None,
        _success_queue=None,
        _failure_queue=None,
    ):
        """
        Handles add_image call.

        Args:
            collection_id (str): Collection ID.
            data (dict): Helios asset.
            _session (aiohttp.ClientSession): Session instance.
            _success_queue (asyncio.Queue): Queue for successful calls.
            _failure_queue (asyncio.Queue): Queue for unsuccessful calls.

        """

        call_params = locals()

        header = {'name': 'Content-Type', 'value': 'application/x-www-form-urlencoded'}
        post_url = '{}/collections/{}/images'.format(self._base_api_url, collection_id)

        try:
            async with _session.post(
                post_url,
                headers=header,
                data=data,
                raise_for_status=True,
                ssl=self._ssl_verify,
            ) as resp:
                resp_json = await resp.json()
        except Exception as e:
            logger.exception('Failed to POST %s.', post_url)
            await _failure_queue.put(
                Record(url=post_url, parameters=call_params, error=e)
            )
            return

        await _success_queue.put(
            Record(url=post_url, parameters=call_params, content=resp_json)
        )

    @logging_utils.log_entrance_exit
    async def copy(self, collection_id, new_name):
        """
        Copy a collection and its contents to a new collection.

        Args:
            collection_id (str): Collection ID.
            new_name (str): New collection name.

        Returns:
            str: New collection ID.

        """

        # Get the collection metadata that needs to be copied.
        query_str = '{}/{}/{}'.format(self._base_api_url, self._core_api, collection_id)
        async with aiohttp.ClientSession(headers=self._auth_header) as sess:
            try:
                async with sess.get(query_str, raise_for_status=True) as resp:
                    metadata = await resp.json()
            except Exception:
                logger.exception('Failed to GET collection metadata. %s', query_str)
                raise

        # Get the images that exist in the collection.
        image_names = await self.images(collection_id)

        # Create new collection.
        new_id = await self.create(new_name, metadata['description'], metadata['tags'])

        # Add images to new collection.
        data = [{'collection_id': collection_id, 'image': x} for x in image_names]
        _ = await self.add_image(data, new_id)

        return new_id

    @logging_utils.log_entrance_exit
    async def create(self, name, description, tags=None):
        """
        Create a new collection.

        Args:
            name (str): Display name for the collection.
            description (str): Description for the collection.
            tags (str or list of strs, optional): Optional comma-delimited
                keyword tags to be added to the collection.

        Returns:
            str: New collection ID.

        """

        payload = {'name': name, 'description': description}
        if tags is not None:
            if isinstance(tags, (list, tuple)):
                tags = ','.join(tags)
            payload['tags'] = tags

        header = {'name': 'Content-Type', 'value': 'application/x-www-form-urlencoded'}

        post_url = '{}/{}'.format(self._base_api_url, self._core_api)

        async with aiohttp.ClientSession(headers=self._auth_header) as session:
            async with session.post(
                post_url,
                headers=header,
                data=payload,
                raise_for_status=True,
                ssl=self._ssl_verify,
            ) as resp:
                resp_json = await resp.json()

        return resp_json['collection_id']

    @logging_utils.log_entrance_exit
    async def destroy(self, collection_id):
        """
        Delete an empty collection.

        If the collection is not empty, delete will fail.  Use the
        :meth:`empty <helios.collections_api.Collections.empty>` method to
        remove all imagery before calling this method.

        Args:
            collection_id (str): Collection to delete.

        Returns:
            dict: {ok: true}

        """

        del_url = '{}/{}/{}'.format(self._base_api_url, self._core_api, collection_id)

        async with aiohttp.ClientSession(headers=self._auth_header) as session:
            async with session.delete(
                del_url, raise_for_status=True, ssl=self._ssl_verify
            ) as resp:
                return await resp.json()

    @logging_utils.log_entrance_exit
    async def empty(self, collection_id):
        """
        Bulk remove (up to 1000) images from a collection.

        Args:
            collection_id (str): Collection to empty.

        Returns:
            dict: {ok: true, total: 1000}

        """

        empty_url = '{}/{}/{}/images'.format(
            self._base_api_url, self._core_api, collection_id
        )

        async with aiohttp.ClientSession(headers=self._auth_header) as session:
            async with session.delete(
                empty_url, raise_for_status=True, ssl=self._ssl_verify
            ) as resp:
                return await resp.json()

    @logging_utils.log_entrance_exit
    async def images(self, collection_id, camera=None, old_flag=False):
        """
        Get all image names in a given collection.

        When using the optional camera input parameter only images from that
        camera will be returned.

        Args:
            collection_id (str): Collection ID.
            camera (str, optional): Camera ID to be found.
            old_flag (bool, optional): Flag for finding old format image names.
                When True images that do not contain md5 hashes at the start of
                their name will be found.

        Returns:
            list of strs: Image names.

        """

        mark_img = ''

        if camera is not None:
            if not old_flag:
                md5_str = hashlib.md5(camera.encode('utf-8')).hexdigest()
                camera = md5_str[0:4] + '-' + camera
            mark_img = camera

        good_images = []
        while True:
            results = await self.show(collection_id, marker=mark_img)

            # Gather images.
            images_found = results.images

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

        return good_images

    async def index(self, **kwargs):
        """
        Get collections matching the provided spatial, text, or metadata filters.

        The maximum skip value is 4000. If this is reached, truncated results
        will be returned. You will need to refine your query to avoid this.

        .. _collections_index_documentation: https://helios.earth/developers/api/collections/#index

        Args:
            **kwargs: Any keyword arguments found in the collections_index_documentation_.

        Returns:
            tuple: A tuple containing:
                feature_collection (:class:`CollectionsFeatureCollection <helios.collections_api.CollectionsFeatureCollection>`):
                    Collections feature collection.
                failed (list of :class:`Record <helios.core.structure.Record>`):
                    Failed API call records.

        """
        succeeded, failed = await super().index(**kwargs)

        content = []
        for record in succeeded:
            for feature in record.content['results']:
                content.append(CollectionsFeature(feature))

        return CollectionsFeatureCollection(content), failed

    @logging_utils.log_entrance_exit
    async def remove_image(self, names, collection_id):
        """
        Remove images from a collection.

        Args:
            names (str or list of strs): List of image names to be removed.
            collection_id (str): Collection ID to remove images from.

        Returns:
            tuple: A tuple containing:
                succeeded (list of :class:`Record <helios.core.structure.Record>`):
                    Successful API call records.
                failed (list of :class:`Record <helios.core.structure.Record>`):
                    Failed API call records.

        """
        if not isinstance(names, (list, tuple)):
            names = [names]

        success_queue = asyncio.Queue()
        failure_queue = asyncio.Queue()
        async with aiohttp.ClientSession(headers=self._auth_header) as session:
            worker = functools.partial(
                self._bound_remove_image_worker,
                collection_id,
                _session=session,
                _success_queue=success_queue,
                _failure_queue=failure_queue,
            )
            tasks = [worker(name) for name in names]
            await asyncio.gather(*tasks)

        succeeded = self._get_all_items(success_queue)
        failed = self._get_all_items(failure_queue)

        return succeeded, failed

    async def _bound_remove_image_worker(self, *args, **kwargs):
        async with self._async_semaphore:
            return await self._remove_image_worker(*args, **kwargs)

    async def _remove_image_worker(
        self,
        collection_id,
        name,
        _session=None,
        _success_queue=None,
        _failure_queue=None,
    ):
        """
        Handles remove_image call.

        Args:
            collection_id (str): Collection ID.
            name (dict): Helios asset.
            _session (aiohttp.ClientSession): Session instance.
            _success_queue (asyncio.Queue): Queue for successful calls.
            _failure_queue (asyncio.Queue): Queue for unsuccessful calls.

        """

        call_params = locals()

        del_url = '{}/{}/{}/images/{}'.format(
            self._base_api_url, self._core_api, collection_id, name
        )

        try:
            async with _session.delete(
                del_url, raise_for_status=True, ssl=self._ssl_verify
            ) as resp:
                resp_json = await resp.json()
        except Exception as e:
            logger.exception('Failed to DELETE %s.', del_url)
            await _failure_queue.put(
                Record(url=del_url, parameters=call_params, error=e)
            )
            return

        await _success_queue.put(
            Record(url=del_url, parameters=call_params, content=resp_json)
        )

    @logging_utils.log_entrance_exit
    async def show(self, collection_id, limit=200, marker=None):
        """
        Get the attributes and image list for collections.

        The results will also contain image names available in the collection.
        These are limited to a maximum of 200 per query.

        Args:
            collection_id (str): Collection ID.
            limit (int, optional): Number of image names to be returned with
                each response. Defaults to 200. Max value of 200 is allowed.
            marker (str, optional): Pagination marker. If the marker is an
                exact match to an existing image, the next image after the
                marker will be the first image returned. Therefore, for normal
                linked list pagination, specify the last image name from the
                current response as the marker value in the next request.
                Partial file names may be specified, in which case the first
                matching result will be the first image returned.

        Returns:
            :class:`CollectionsFeature <helios.collections_api.CollectionsFeature>`:
                A single collection feature.

        """
        if not isinstance(collection_id, str):
            raise TypeError(
                'Expected collection_id to be a str but found {} '
                'instead'.format(type(collection_id))
            )

        params_str = self._parse_query_inputs(**dict(limit=limit, marker=marker))
        query_str = '{}/{}/{}?{}'.format(
            self._base_api_url, self._core_api, collection_id, params_str
        )

        async with aiohttp.ClientSession(headers=self._auth_header) as session:
            async with session.get(
                query_str, raise_for_status=True, ssl=self._ssl_verify
            ) as resp:
                resp_json = await resp.json()

        return CollectionsFeature(resp_json)

    async def show_image(
        self, collection_id, image_names, out_dir=None, return_image_data=False
    ):
        """
        Get images from a collection.

        Args:
            collection_id (str): Collection ID to add images into.
            image_names (str or list of strs): Image names.
            out_dir (optional, str): Directory to write images to.  Defaults to
                None.
            return_image_data (optional, bool): If True images will be
                available as PIL images in the returned ImageRecords.
                Defaults to False.

        Returns:
            tuple: A tuple containing:
                images (list of :class:`ImageRecord <helios.core.structure.ImageRecord>`):
                    All received images.
                failed (:class:`ImageRecord <helios.core.structure.ImageRecord>`):
                    Failed API calls.

        """
        succeeded, failed = await super().show_image(
            collection_id,
            image_names,
            out_dir=out_dir,
            return_image_data=return_image_data,
        )

        return succeeded, failed

    @logging_utils.log_entrance_exit
    async def update(self, collections_id, name=None, description=None, tags=None):
        """
        Update a collection.

        Args:
            collections_id (str): Collection ID.
            name (str, optional): Name to be changed to.
            description (str, optional): Description to be changed to.
            tags (str or list of strs, optional): Optional comma-delimited
                keyword tags to be changed to.

        Returns:
            dict: Json response.

        """
        if name is None and description is None and tags is None:
            raise ValueError(
                'Update requires at least one keyword argument to be used.'
            )

        # Compose parms block
        parms = {}
        if name is not None:
            parms['name'] = name
        if description is not None:
            parms['description'] = description
        if tags is not None:
            if isinstance(tags, (list, tuple)):
                tags = ','.join(tags)
            parms['tags'] = tags

        header = {'name': 'Content-Type', 'value': 'application/x-www-form-urlencoded'}

        patch_url = '{}/{}/{}'.format(
            self._base_api_url, self._core_api, collections_id
        )

        async with aiohttp.ClientSession(headers=self._auth_header) as session:
            async with session.patch(
                patch_url,
                data=parms,
                headers=header,
                raise_for_status=True,
                ssl=self._ssl_verify,
            ) as resp:
                return await resp.json()


class CollectionsFeature:
    """
    Individual Collection JSON result.

    Attributes:
        bucket (str): 'bucket' value for the result.
        created_at (str): 'city' value for the result.
        description (str): 'created_at' value for the result.
        id (str): '_id' value for the result.
        images (list of strs): 'images' value for the result.
        json (dict): Raw JSON result.
        name (str): 'name' value for the result.
        tags (list of strs): 'tags' value for the result.
        updated_at (str): 'updated_at' value for the result.
        user_id (str): 'user_id' value for the result.

    """

    def __init__(self, feature):
        self.json = feature

    @property
    def bucket(self):
        return self.json.get('bucket')

    @property
    def created_at(self):
        return self.json.get('created_at')

    @property
    def description(self):
        return self.json.get('description')

    @property
    def id(self):
        return self.json.get('_id')

    @property
    def images(self):
        return self.json.get('images')

    @property
    def name(self):
        return self.json.get('name')

    @property
    def tags(self):
        return self.json.get('tags')

    @property
    def updated_at(self):
        return self.json.get('updated_at')

    @property
    def user_id(self):
        return self.json.get('user_id')


class CollectionsFeatureCollection:
    """
    Collection of features obtained via the Collections API.

    Convenience properties are available to extract values from every feature.

    Attributes:
        features (list of :class:`CollectionsFeature <helios.collections_api.CollectionsFeature>`):
            All features returned from a query.

    """

    def __init__(self, features):
        self.features = features

    @property
    def bucket(self):
        """'bucket' values for every result."""
        return [x.bucket for x in self.features]

    @property
    def created_at(self):
        """'city' values for every result."""
        return [x.created_at for x in self.features]

    @property
    def description(self):
        """'created_at' values for every result."""
        return [x.description for x in self.features]

    @property
    def id(self):
        """'_id' values for every result."""
        return [x.id for x in self.features]

    @property
    def json(self):
        """Raw 'json' for every feature."""
        return [x.json for x in self.features]

    @property
    def name(self):
        """'name' values for every result."""
        return [x.name for x in self.features]

    @property
    def tags(self):
        """'tags' values for every result."""
        return [x.tags for x in self.features]

    @property
    def updated_at(self):
        """'updated_at' values for every result."""
        return [x.updated_at for x in self.features]

    @property
    def user_id(self):
        """'user_id' values for every result."""
        return [x.user_id for x in self.features]
