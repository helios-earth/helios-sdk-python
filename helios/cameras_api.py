"""
Helios Cameras API.

Methods are meant to represent the core functionality in the developer
documentation.  Some may have additional functionality for convenience.

"""
import logging

import aiohttp
from dateutil.parser import parse
from helios.core.mixins import SDKCore, ShowMixin, ShowImageMixin, IndexMixin
from helios.core.structure import ImageCollection
from helios.utilities import logging_utils

logger = logging.getLogger(__name__)


class Cameras(ShowImageMixin, ShowMixin, IndexMixin, SDKCore):
    """The Cameras API provides access to all cameras in the Helios Network."""

    _core_api = 'cameras'

    def __init__(self, session=None):
        """
        Initialize Cameras instance.

        Args:
            session (helios.Session object, optional): An instance of the
                Session. Defaults to None. If unused a session will be
                created for you.

        """
        super(Cameras, self).__init__(session=session)

    @logging_utils.log_entrance_exit
    async def images(self, camera_id, start_time, end_time=None, limit=500):
        """
        Get the image times available for a given camera in the media cache.

        The media cache contains all recent images archived by Helios, either
        for internal analytics or for end user recording purposes.

        Args:
            camera_id (str): Camera ID.
            start_time (str): Starting image timestamp, specified in UTC as an
                ISO 8601 string (e.g. 2014-08-01 or 2014-08-01T12:34:56.000Z).
            end_time (str, optional): Ending image timestamp, specified in UTC
                as an ISO 8601 string (e.g. 2014-08-01 or 2014-08-01T12:34:56.000Z).
            limit (int, optional): Number of images to be returned, up to a max
                of 500. Defaults to 500.

        Returns:
            list of strs: Image times.

        """

        if end_time:
            end = parse(end_time).utctimetuple()
        else:
            end = None

        async with aiohttp.ClientSession(headers=self._auth_header) as session:
            image_times = []
            while True:
                query_str = '{}/{}/{}/images?time={}&limit={}'.format(self._base_api_url,
                                                                      self._core_api,
                                                                      camera_id,
                                                                      start_time,
                                                                      limit)
                # Get image times available.
                try:
                    async with session.get(query_str,
                                           raise_for_status=True,
                                           ssl=self._ssl_verify) as resp:
                        resp_json = await resp.json()
                except aiohttp.ClientError:
                    logger.exception('Failed to GET %s.', query_str)
                    raise

                times = resp_json['times']

                # Return now if no end_time was provided.
                if end_time is None:
                    image_times.extend(times)
                    break

                # Parse the last time and break if no times were found
                try:
                    last = parse(times[-1]).utctimetuple()
                except IndexError:
                    break

                # the last image is still newer than the end time, keep looking
                if last < end:
                    if len(times) > 1:
                        image_times.extend(times[0:-1])
                        start_time = times[-1]
                    else:
                        image_times.extend(times)
                        break
                # The end time is somewhere in between.
                elif last > end:
                    good_times = [x for x in times if parse(x).utctimetuple() < end]
                    image_times.extend(good_times)
                    break
                else:
                    image_times.extend(times)
                    break

            if not image_times:
                logger.warning('No images were found for %s in the %s to %s range.',
                               camera_id, start_time, end_time)

        return image_times

    async def index(self, **kwargs):
        """
        Get cameras matching the provided spatial, text, or
        metadata filters.

        The maximum skip value is 4000. If this is reached, truncated results
        will be returned. You will need to refine your query to avoid this.

        .. _cameras_index_documentation: https://helios.earth/developers/api/cameras/#index

        Args:
            **kwargs: Any keyword arguments found in the cameras_index_documentation_.

        Returns:
             :class:`CamerasFeatureCollection <helios.cameras_api.CamerasFeatureCollection>`

        """

        succeeded, failed = await super(Cameras, self).index(**kwargs)

        content = []
        for record in succeeded:
            for feature in record.content['features']:
                content.append(CamerasFeature(feature))

        return CamerasFeatureCollection(content), failed

    async def show(self, camera_ids):
        """
        Get attributes for cameras.

        Args:
            camera_ids (str or list of strs): Helios camera ID(s).

        Returns:
            :class:`CamerasFeatureCollection <helios.cameras_api.CamerasFeatureCollection>`

        """

        succeeded, failed = await super(Cameras, self).show(camera_ids)

        content = []
        for record in succeeded:
            content.append(CamerasFeature(record.content))

        return CamerasFeatureCollection(content), failed

    async def show_image(self, camera_id, times, out_dir=None, return_image_data=False):
        """
        Get images from the media cache.

        The media cache contains all recent images archived by Helios, either
        for internal analytics or for end user recording purposes.

        Args:
            camera_id (str): Camera ID.
            times (str or list of strs): Image times, specified in UTC as
                an ISO 8601 string (e.g. 2017-08-01 or 2017-08-01T12:34:56.000Z).
                The image with the closest matching timestamp will be returned.
            out_dir (optional, str): Directory to write images to.  Defaults to
                None.
            return_image_data (optional, bool): If True, PIL Images will be
                returned.

        Returns:
            :class:`ImageCollection <helios.core.structure.ImageCollection>`

        """

        succeeded, failed = await super(Cameras, self).show_image(
            camera_id, times, out_dir=out_dir, return_image_data=return_image_data)

        return ImageCollection(succeeded), failed


class CamerasFeature(object):
    """
    Individual Camera GeoJSON feature.

    Attributes:
        city (str): 'city' value for the feature.
        country (str): 'country' value for the feature.
        description (str): 'description' value for the feature.
        direction (str): 'direction' value for the feature.
        id (str): 'id' value for the feature.
        json (dict): Raw 'json' for the feature.
        region (str): 'region' value for the feature.
        state (str): 'state' value for the feature.
        video (bool): 'video' value for the feature.

    """

    def __init__(self, feature):
        self.json = feature

        # Use dict.get built-in to guarantee all values will be initialized.
        self.city = feature['properties'].get('city')
        self.coordinates = feature['geometry'].get('coordinates')
        self.country = feature['properties'].get('country')
        self.description = feature['properties'].get('description')
        self.direction = feature['properties'].get('direction')
        self.id = feature.get('id')
        self.region = feature['properties'].get('region')
        self.state = feature['properties'].get('state')
        self.video = feature['properties'].get('video')


class CamerasFeatureCollection(object):
    """
    Collection of GeoJSON features obtained via the Cameras API.

    Convenience properties are available to extract values from every feature.

    Attributes:
        features (list of :class:`CamerasFeature <helios.cameras_api.CamerasFeature>`):
            All features returned from a query.

    """

    def __init__(self, features):
        self.features = features

    @property
    def city(self):
        """'city' values for every feature."""
        return [x.city for x in self.features]

    @property
    def coordinates(self):
        """'coordinate' values for every feature."""
        return [x.coordinates for x in self.features]

    @property
    def country(self):
        """'country' values for every feature."""
        return [x.country for x in self.features]

    @property
    def description(self):
        """'description' values for every feature."""
        return [x.description for x in self.features]

    @property
    def direction(self):
        """'direction' values for every feature."""
        return [x.direction for x in self.features]

    @property
    def id(self):
        """'id' values for every feature."""
        return [x.id for x in self.features]

    @property
    def json(self):
        """Raw 'json' for every feature."""
        return [x.json for x in self.features]

    @property
    def region(self):
        """'region' values for every feature."""
        return [x.region for x in self.features]

    @property
    def state(self):
        """'state' values for every feature."""
        return [x.state for x in self.features]

    @property
    def video(self):
        """'video' values for every feature."""
        return [x.video for x in self.features]
