"""
Helios Cameras API.

Methods are meant to represent the core functionality in the developer
documentation.  Some may have additional functionality for convenience.

"""
import logging

from dateutil.parser import parse
from helios.core import SDKCore, ShowMixin, ShowImageMixin, IndexMixin
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

    def index(self, **kwargs):
        """
        Return a list of cameras matching the provided spatial, text, or
        metadata filters.

        The maximum skip value is 4000. If this is reached, truncated results
        will be returned. You will need to refine your query to avoid this.

        .. _cameras_index_documentation: https://helios.earth/developers/api/cameras/#index

        Args:
            **kwargs: Any keyword arguments found in the cameras_index_documentation_.

        Returns:
             list: GeoJSON feature collections.

        """
        return super(Cameras, self).index(**kwargs)

    @logging_utils.log_entrance_exit
    def images(self, camera_id, start_time, limit=500):
        """
        Return the image times available for a given camera in the media cache.

        The media cache contains all recent images archived by Helios, either
        for internal analytics or for end user recording purposes.

        Args:
            camera_id (str): Camera ID.
            start_time (str): Starting image timestamp, specified in UTC as an
                ISO 8601 string (e.g. 2014-08-01 or 2014-08-01T12:34:56.000Z).
            limit (int, optional): Number of images to be returned, up to a max
                of 500. Defaults to 500.


        Returns:
            sequence of strs: Image times.

        """
        query_str = '{}/{}/{}/images?time={}&limit={}'.format(self._base_api_url,
                                                              self._core_api,
                                                              camera_id,
                                                              start_time,
                                                              limit)

        resp = self._request_manager.get(query_str).json()

        return resp['times']

    @logging_utils.log_entrance_exit
    def images_range(self, camera_id, start_time, end_time, limit=500):
        """
        Return image times available in a given time range.

        The media cache contains all recent images archived by Helios, either
        for internal analytics or for end user recording purposes.

        Args:
            camera_id (str): Camera ID.
            start_time (str): Starting image timestamp, specified in UTC as an
                ISO 8601 string (e.g. 2014-08-01 or 2014-08-01T12:34:56.000Z).
            end_time (str): Ending image timestamp, specified in UTC as an
                ISO 8601 string (e.g. 2014-08-01 or 2014-08-01T12:34:56.000Z).
            limit (int, optional): Number of images to be returned, up to a max
                of 500.  Defaults to 500.

        Returns:
            sequence of strs: Image times.

        """
        end = parse(end_time).utctimetuple()
        image_times = []
        while True:
            times = self.images(camera_id, start_time, limit=limit)

            try:
                last = parse(times[-1]).utctimetuple()
            except IndexError:
                break

            # the last image is still newer than our end time, keep looking
            if last < end:
                if len(times) > 1:
                    image_times.extend(times[0:-1])
                    start_time = times[-1]
                else:
                    image_times.extend(times)
                    break
            elif last > end:
                good_times = [x for x in times if parse(x).utctimetuple() < end]
                image_times.extend(good_times)
                break
            else:
                image_times.extend(times)
                break

        if len(image_times) == 0:
            self._logger.warning('No images were found for %s in the %s to %s range.',
                                 camera_id, start_time, end_time)

        return image_times

    def show_image(self, camera_id, times, out_dir=None, return_image_data=False):
        """
        Return a single image from the media cache.

        The media cache contains all recent images archived by Helios, either
        for internal analytics or for end user recording purposes.

        Args:
            camera_id (str): Camera ID.
            times (str or sequence of strs): Image times, specified in UTC as an ISO 8601
                string (e.g. 2017-08-01 or 2017-08-01T12:34:56.000Z). The
                image with the closest matching timestamp will be returned.
            out_dir (optional, str): Directory to write images to.  Defaults to
                None.
            return_image_data (optional, bool): If True images will be returned
                as numpy.ndarrays.  Defaults to False.

        Returns:
            sequence of :class:`ShowImageRecord <helios.core.records.ShowImageRecord>`

        """
        return super(Cameras, self).show_image(camera_id, times, out_dir=out_dir,
                                               return_image_data=return_image_data)
