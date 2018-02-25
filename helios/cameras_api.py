"""
Helios Cameras API.

Methods are meant to represent the core functionality in the developer
documentation.  Some may have additional functionality for convenience.

"""
import logging
from collections import namedtuple

from dateutil.parser import parse

from helios.core.mixins import SDKCore, ShowMixin, ShowImageMixin, IndexMixin
from helios.core.structure import ContentCollection, RecordCollection
from helios.utilities import logging_utils


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
        self._logger = logging.getLogger(__name__)

    @logging_utils.log_entrance_exit
    def images(self, camera_id, start_time, end_time=None, limit=500):
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
            sequence of strs: Image times.

        """
        if end_time:
            end = parse(end_time).utctimetuple()
        else:
            end = None

        image_times = []
        while True:
            query_str = '{}/{}/{}/images?time={}&limit={}'.format(self._base_api_url,
                                                                  self._core_api,
                                                                  camera_id,
                                                                  start_time,
                                                                  limit)
            # Get image times available.
            resp = self._request_manager.get(query_str)
            times = resp.json()['times']

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
            self._logger.warning('No images were found for %s in the %s to %s range.',
                                 camera_id, start_time, end_time)

        return image_times

    def index(self, **kwargs):
        """
        Get cameras matching the provided spatial, text, or
        metadata filters.

        The maximum skip value is 4000. If this is reached, truncated results
        will be returned. You will need to refine your query to avoid this.

        .. _cameras_index_documentation: https://helios.earth/developers/api/cameras/#index

        Args:
            **kwargs: Any keyword arguments found in the cameras_index_documentation_.

        Returns:
             :class:`IndexResults <helios.cameras_api.IndexResults>`

        """
        return IndexResults(super(Cameras, self).index(**kwargs))

    def show(self, camera_ids):
        """
        Get attributes for cameras.

        Args:
            camera_ids (str or sequence of strs): Helios camera ID(s).

        Returns:
            :class:`ShowResults <helios.cameras_api.ShowResults>`

        """
        return ShowResults(super(Cameras, self).show(camera_ids))

    def show_image(self, camera_id, times, out_dir=None, return_image_data=False):
        """
        Get images from the media cache.

        The media cache contains all recent images archived by Helios, either
        for internal analytics or for end user recording purposes.

        Args:
            camera_id (str): Camera ID.
            times (str or sequence of strs): Image times, specified in UTC as
                an ISO 8601 string (e.g. 2017-08-01 or 2017-08-01T12:34:56.000Z).
                The image with the closest matching timestamp will be returned.
            out_dir (optional, str): Directory to write images to.  Defaults to
                None.
            return_image_data (optional, bool): If True images will be returned
                as numpy.ndarrays.  Defaults to False.

        Returns:
            :class:`ShowImageResults <helios.cameras_api.ShowImageResults>`

        """
        return ShowImageResults(super(Cameras, self).show_image(
            camera_id, times, out_dir=out_dir, return_image_data=return_image_data))


class IndexResults(ContentCollection):
    """Index results for the Cameras API."""

    def __init__(self, geojson):
        super(IndexResults, self).__init__(geojson)

    def _build(self):
        """
        Combine GeoJSON features into the content attribute.

        Each feature will be used to create a Feature object.  The feature
        object will contain easy access to some of the GeoJSON attributes.

        This also allows the user to iterate and select based on Feature
        attributes. e.g. [x for x in index_results if x.video]

        """
        feature_tuple = namedtuple('Feature', ['city', 'country', 'description',
                                               'id', 'json', 'region', 'state',
                                               'video'])
        self.content = []
        for feature_collection in self._raw:
            for feature in feature_collection['features']:
                # Use dict.get built-in to guarantee all values will be initialized.
                city = feature['properties'].get('city')
                country = feature['properties'].get('country')
                description = feature['properties'].get('description')
                id_ = feature.get('id')
                region = feature['properties'].get('region')
                state = feature['properties'].get('state')
                video = feature['properties'].get('video')
                self.content.append(feature_tuple(city=city,
                                                  country=country,
                                                  description=description,
                                                  id=id_,
                                                  json=feature,
                                                  region=region,
                                                  state=state,
                                                  video=video))

    @property
    def city(self):
        """'city' values for every feature."""
        return [x.city for x in self.content]

    @property
    def country(self):
        """'country' values for every feature."""
        return [x.country for x in self.content]

    @property
    def description(self):
        """'description' values for every feature."""
        return [x.description for x in self.content]

    @property
    def id(self):
        """'id' values for every feature."""
        return [x.id for x in self.content]

    @property
    def json(self):
        """Raw 'json' for every feature."""
        return [x.json for x in self.content]

    @property
    def region(self):
        """'region' values for every feature."""
        return [x.region for x in self.content]

    @property
    def state(self):
        """'state' values for every feature."""
        return [x.state for x in self.content]

    @property
    def video(self):
        """'video' values for every feature."""
        return [x.video for x in self.content]


class ShowImageResults(RecordCollection):
    """Show_image results for the Cameras API."""

    def __init__(self, image_records):
        super(ShowImageResults, self).__init__(image_records)

    def _build(self):
        """
        Combine all ImageRecord instance content.

        All content will be image data in this case, if return_image_data was
        True.

        """
        self.content = [x.content for x in self._raw]

    @property
    def image_data(self):
        """Image data if return_image_data was True."""
        return self.content

    @property
    def output_file(self):
        """Full paths to all written images."""
        return [x.output_file for x in self._raw if x.ok]

    @property
    def name(self):
        """Names of all images."""
        return [x.name for x in self._raw if x.ok]


class ShowResults(RecordCollection):
    """Show results for the Cameras API."""

    def __init__(self, records):
        super(ShowResults, self).__init__(records)

    def _build(self):
        """Combine GeoJSON content from within each record."""
        feature_tuple = namedtuple('Feature', ['city', 'country', 'description',
                                               'direction', 'id', 'json', 'region',
                                               'state', 'video'])
        self.content = []
        for record in self._raw:
            feature = record.content
            # Use dict.get built-in to guarantee all values will be initialized.
            city = feature['properties'].get('city')
            country = feature['properties'].get('country')
            description = feature['properties'].get('description')
            direction = feature['properties'].get('direction')
            id_ = feature.get('id')
            region = feature['properties'].get('region')
            state = feature['properties'].get('state')
            video = feature['properties'].get('video')
            self.content.append(feature_tuple(city=city,
                                              country=country,
                                              description=description,
                                              direction=direction,
                                              id=id_,
                                              json=feature,
                                              region=region,
                                              state=state,
                                              video=video))

    @property
    def city(self):
        """'city' values for every feature."""
        return [x.city for x in self.content]

    @property
    def country(self):
        """'country' values for every feature."""
        return [x.country for x in self.content]

    @property
    def description(self):
        """'description' values for every feature."""
        return [x.description for x in self.content]

    @property
    def direction(self):
        """'direction' values for every feature."""
        return [x.direction for x in self.content]

    @property
    def id(self):
        """'id' values for every feature."""
        return [x.id for x in self.content]

    @property
    def json(self):
        """Raw 'json' for every feature."""
        return [x.json for x in self.content]

    @property
    def region(self):
        """'region' values for every feature."""
        return [x.region for x in self.content]

    @property
    def state(self):
        """'state' values for every feature."""
        return [x.state for x in self.content]

    @property
    def video(self):
        """'video' values for every feature."""
        return [x.video for x in self.content]
