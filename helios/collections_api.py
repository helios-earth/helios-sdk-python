"""
Helios Collections API.

Methods are meant to represent the core functionality in the developer
documentation.  Some may have additional functionality for convenience.

"""

import hashlib
import logging
from collections import namedtuple

import requests

from helios.core import SDKCore, IndexMixin, ShowImageMixin, DownloadImagesMixin
from helios.utilities import logging_utils


class Collections(DownloadImagesMixin, ShowImageMixin, IndexMixin, SDKCore):
    """
    The Collections API allows users to group and organize individual image
    frames.

    Collections are intended to be short-lived resources and will be accessible
    for 90 days from the time the collection was created. After that time
    period has expired, the collection and all associated imagery will be
    removed from the system.

    """
    _core_api = 'collections'

    def __init__(self, session=None):
        """
        Initialize Collection instance.

        Args:
            session (helios.Session object, optional): An instance of the
                Session. Defaults to None. If unused a session will be
                created for you.

        """
        super(Collections, self).__init__(session=session)
        self._logger = logging.getLogger(__name__)

    def index(self, **kwargs):
        """
        Return a list of collections matching the provided spatial, text, or
        metadata filters.

        The maximum skip value is 4000. If this is reached, truncated results
        will be returned. You will need to refine your query to avoid this.

        Args:
            **kwargs: Any keyword arguments found in the documentation.

        Returns:
             list: GeoJSON feature collections.

        """
        return super(Collections, self).index(**kwargs)

    @logging_utils.log_entrance_exit
    def show(self, collection_id, limit=200, marker=None):
        """
        Return the attributes and image list for a single collection.

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
            dict: Dictionary containing collection attributes and image list.

        """
        params_str = self._parse_query_inputs(dict(limit=limit, marker=marker))
        query_str = '{}/{}/{}?{}'.format(self._base_api_url,
                                         self._core_api,
                                         collection_id,
                                         params_str)

        resp = self._request_manager.get(query_str)

        return resp.json()

    @logging_utils.log_entrance_exit
    def create(self, name, description, tags=None):
        """
        Create a new collection.

        Args:
            name (str): Display name for the collection.
            description (str): Description for the collection.
            tags (str or sequence of strs, optional): Optional comma-delimited
                keyword tags to be added to the collection.

        Returns:
            str: New collection ID.

        """
        # need to strip out the Bearer to work with a POST for collections
        post_token = self._request_manager.auth_token['value'].replace('Bearer ', '')

        # Compose parms block
        parms = {'name': name, 'description': description, 'access_token': post_token}
        if tags is not None:
            if isinstance(tags, (list, tuple)):
                tags = ','.join(tags)
            parms['tags'] = tags

        header = {'name': 'Content-Type',
                  'value': 'application/x-www-form-urlencoded'}

        post_url = '{}/{}'.format(self._base_api_url, self._core_api)

        resp = self._request_manager.post(post_url, headers=header, data=parms).json()

        return resp['collection_id']

    @logging_utils.log_entrance_exit
    def update(self, collections_id, name=None, description=None, tags=None):
        """
        Update a collection.

        Args:
            collections_id (str): Collection ID.
            name (str, optional): Name to be changed to.
            description (str, optional): Description to be changed to.
            tags (str or sequence of strs, optional): Optional comma-delimited
                keyword tags to be changed to.

        """
        if name is None and description is None and tags is None:
            raise ValueError('Update requires at least one keyword argument '
                             'to be used.')

        # need to strip out the Bearer to work with a PATCH for collections
        patch_token = self._request_manager.auth_token['value'].replace('Bearer ', '')

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
        parms['access_token'] = patch_token

        header = {'name': 'Content-Type',
                  'value': 'application/x-www-form-urlencoded'}

        patch_url = '{}/{}/{}'.format(self._base_api_url,
                                      self._core_api,
                                      collections_id)

        self._request_manager.patch(patch_url, headers=header, data=parms)

    @logging_utils.log_entrance_exit
    def images(self, collection_id, camera=None, old_flag=False):
        """
        Returns all image names in a given collection.

        When using the optional camera input parameter only images from that
        camera will be returned.

        Args:
            collection_id (str): Collection ID.
            camera (str, optional): Camera ID to be found.
            old_flag (bool, optional): Flag for finding old format image names.
                When True images that do not contain md5 hashes at the start of
                their name will be found.

        Returns:
            sequence of strs: Image names.

        """
        mark_img = ''

        if camera is not None:
            if not old_flag:
                md5_str = hashlib.md5(camera.encode('utf-8')).hexdigest()
                camera = md5_str[0:4] + '-' + camera
            mark_img = camera

        good_images = []
        while True:
            results = self.show(collection_id, marker=mark_img)

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

        return good_images

    def show_image(self, collection_id,
                   image_names,
                   out_dir=None,
                   return_image_data=False):
        """
        Return image URLs from a collection.

        Args:
            collection_id (str): Collection ID.
            image_names (str or sequence of strs): Image names.
            out_dir (optional, str): Directory to write images to.
            return_image_data (optional, bool): If True images will be returned
                as numpy.ndarrays.

        Returns:
            sequence of strs: Image URLs.

        """
        return super(Collections, self).show_image(collection_id,
                                                   image_names,
                                                   out_dir=out_dir,
                                                   return_image_data=return_image_data)

    @logging_utils.log_entrance_exit
    def add_image(self, collection_id, assets):
        """
        Add images to a collection from Helios assets.

        `assets` dictionary templates:

        .. code-block:: python

            # Asset examples that can be included in the `assets` input list.
            {'camera_id': ''}
            {'camera_id': '', 'time': ''}
            {'observation_id': ''}
            {'collection_is': '', 'image': ''}

        Usage example:

        .. code-block:: python

            import helios
            collections = helios.Collections()
            camera_id = '...'
            times = [...] # List of image times.
            destination_id = '...'
            data = [{'camera_id': camera_id, 'time': x} for x in times]
            collections.add_image(destination_id, data)

        Args:
            collection_id (str): Collection ID.
            assets (dict or sequence of dicts): Data containing any of these
                payloads (camera_id), (camera_id, time), (observation_id),
                (collection_id, image). E.g. data =
                [{'camera_id': 'cam_01', time: '2017-01-01T00:00:000Z'}]

        Returns:
            (sequence of dicts): If errors do occur then the data that caused
            the errors will be returned.

        """
        assert isinstance(assets, (list, tuple, dict))

        if isinstance(assets, dict):
            assets = [assets]

        # Create messages for worker.
        Message = namedtuple('Message', ['collection_id', 'data'])
        messages = [Message(collection_id, x) for x in assets]

        # Process messages using the worker function.
        results = self._process_messages(self.__add_image_worker, messages)

        # Extract failures.
        failures = [y for x, y in zip(results, assets) if x == -1]

        # Determine how many were successful
        n_images = len(assets)
        n_successful = n_images - len(failures)
        message = 'addImage({} out of {} successful)'.format(n_successful, n_images)

        if n_successful == 0:
            self._logger.error(message)
            return -1
        elif n_successful < n_images:
            self._logger.warning(message)
        else:
            self._logger.info(message)

        return failures

    def __add_image_worker(self, msg):
        """msg must contain collection_id and data"""
        # need to strip out the Bearer to work with a POST for collections
        post_token = self._request_manager.auth_token['value'].replace('Bearer ', '')

        # Compose post request
        parms = {'access_token': post_token}
        parms.update(msg.data)

        header = {'name': 'Content-Type',
                  'value': 'application/x-www-form-urlencoded'}
        post_url = '{}/collections/{}/images'.format(self._base_api_url,
                                                     msg.collection_id)

        try:
            self._request_manager.post(post_url, headers=header, data=parms)
        except requests.exceptions.RequestException:
            return -1

    @logging_utils.log_entrance_exit
    def remove_image(self, collection_id, names):
        """
        Remove images from a collection.

        Args:
            collection_id (str): Collection ID.
            names (str or sequence of strs): List of image names to be removed.

        Returns:
            (sequence of strs): If errors do occur then the data that caused
            the errors will be returned.

        """
        if not isinstance(names, (list, tuple)):
            names = [names]

        # Create messages for worker.
        Message = namedtuple('Message', ['collection_id', 'img_name'])
        messages = [Message(collection_id, x) for x in names]

        # Process messages using the worker function.
        results = self._process_messages(self.__remove_image_worker, messages)

        # Extract failures.
        failures = [y for x, y in zip(results, names) if x == -1]

        # Determine how many were successful
        n_names = len(names)
        n_successful = n_names - len(failures)
        message = 'removeImage({} out of {} successful)'.format(n_successful, n_names)

        if n_successful == 0:
            self._logger.error(message)
            return -1
        elif n_successful < n_names:
            self._logger.warning(message)
        else:
            self._logger.info(message)

        return failures

    def __remove_image_worker(self, msg):
        """msg must contain collection_id and img_name"""
        query_str = '{}/{}/{}/images/{}'.format(self._base_api_url,
                                                self._core_api,
                                                msg.collection_id,
                                                msg.img_name)

        try:
            self._request_manager.delete(query_str)
        except requests.exceptions.RequestException:
            return -1

    @logging_utils.log_entrance_exit
    def copy(self, collection_id, new_name):
        """
        Copy a collection and its contents to a new collection.

        Args:
            collection_id (str): Collection ID.
            new_name (str): New collection name.

        Returns:
            str: New collection ID.

        """
        # Get the collection metadata that needs to be copied.
        query_str = '{}/{}/{}'.format(self._base_api_url,
                                      self._core_api,
                                      collection_id)
        metadata = self._request_manager.get(query_str).json()

        # Get the images that exist in the collection.
        image_names = self.images(collection_id)

        # Create new collection.
        new_id = self.create(new_name, metadata['description'], metadata['tags'])

        # Add images to new collection.
        data = [{'collection_id': collection_id, 'image': x} for x in image_names]
        _ = self.add_image(new_id, data)

        return new_id
