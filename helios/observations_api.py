"""
Helios Observations API.

Methods are meant to represent the core functionality in the developer
documentation.  Some may have additional functionality for convenience.

"""
import asyncio
import functools
import logging
import os
from collections import namedtuple, defaultdict
from io import BytesIO

import aiofiles
import aiohttp
from PIL import Image

from helios.core.mixins import SDKCore, IndexMixin, ShowMixin
from helios.core.structure import ImageRecord, ImageCollection
from helios.utilities import logging_utils, parsing_utils

logger = logging.getLogger(__name__)


class Observations(ShowMixin, IndexMixin, SDKCore):
    """
    The Observations API provides ground-truth data generated by the Helios
    analytics.

    """

    _core_api = 'observations'

    def __init__(self, session):
        """
        Initialize Observations instance.

        Args:
            session (helios.HeliosSession): An instance of the
                Session. Defaults to None. If unused a session will be
                created for you.

        """
        super(Observations, self).__init__(session)

    async def index(self, **kwargs):
        """
        Get observations matching the provided spatial, text, or
        metadata filters.

        The maximum skip value is 4000. If this is reached, truncated results
        will be returned. You will need to refine your query to avoid this.

        Usage example:

        .. code-block:: python3

            import helios
            async with helios.HeliosSession() as sess:
                obs_inst = helios.Observations(sess)
                state = 'Maryland'
                bbox = [-169.352,1.137,-1.690,64.008]
                sensors = 'sensors[visibility][min]=0&sensors[visibility][max]=1'
                results, failures = await obs.index(state=state,
                                                    bbox=bbox,
                                                    sensors=sensors)

        Usage example for transitions:

        .. code-block:: python3

            import helios
            async with helios.HeliosSession() as sess:
                obs_inst = helios.Observations(sess)
                # transition from dry/wet to partial/fully-covered snow roads
                sensors = 'sensors[road_weather][data][min]=6&sensors[road_weather][prev][max]=3'
                results, failures = await obs.index(sensors=sensors_query)

        .. _observations_index_documentation: https://helios.earth/developers/api/observations/#index

        Args:
            **kwargs: Any keyword arguments found in the
                observations_index_documentation_.

        Returns:
            tuple: A tuple containing:
                feature_collection (:class:`ObservationsFeatureCollection <helios.observations_api.ObservationsFeatureCollection>`):
                    Observations feature collection.
                failed (list of :class:`Record <helios.core.structure.Record>`):
                    Failed API call records.

        """

        succeeded, failed = await super(Observations, self).index(**kwargs)

        content = []
        for record in succeeded:
            for feature in record.content['features']:
                content.append(ObservationsFeature(feature))

        return ObservationsFeatureCollection(content), failed

    @logging_utils.log_entrance_exit
    async def preview(self, observation_ids, out_dir=None, return_image_data=False):
        """
        Get preview images from observations.

        Args:
            observation_ids (str or list of strs): list of observation IDs.
            out_dir (optional, str): Directory to write images to.  Defaults to
                None.
            return_image_data (optional, bool): If True images will be returned
                as numpy.ndarrays.  Defaults to False.

        Returns:
            tuple: A tuple containing:
                image_collection (:class:`ImageCollection <helios.core.structure.ImageCollection>`):
                    All received images.
                failed (list of :class:`Record <helios.core.structure.Record>`):
                    Failed API calls.

        """

        # Make sure directory exists.
        if out_dir is not None:
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)

        success_queue = asyncio.Queue()
        failure_queue = asyncio.Queue()
        async with aiohttp.ClientSession(headers=self._auth_header) as session:
            worker = functools.partial(
                self._bound_preview_worker, out_dir=out_dir,
                return_image_data=return_image_data,
                _session=session,
                _success_queue=success_queue,
                _failure_queue=failure_queue
            )
            tasks = [worker(id_) for id_ in observation_ids]
            await asyncio.gather(*tasks)

        succeeded = self._get_all_items(success_queue)
        failed = self._get_all_items(failure_queue)

        return ImageCollection(succeeded), failed

    async def _bound_preview_worker(self, *args, **kwargs):
        async with self._async_semaphore:
            return await self._preview_worker(*args, **kwargs)

    async def _preview_worker(
        self,
        observation_id,
        out_dir=None,
        return_image_data=None,
        _session=None,
        _success_queue=None,
        _failure_queue=None,
    ):
        """
        Handles preview calls.

        Args:
            observation_id (str): Observation ID.
            out_dir (str, optional): Optionally write data to a directory.
            return_image_data (bool, optional): Optionally load image data
                into PIL and include in returned data.
            _session (aiohttp.ClientSession): Session instance.
            _success_queue (asyncio.Queue): Queue for successful calls.
            _failure_queue (asyncio.Queue): Queue for unsuccessful calls.

        """

        call_params = locals()

        query_str = '{}/{}/{}/preview'.format(
            self._base_api_url, self._core_api, observation_id
        )

        try:
            async with _session.get(
                query_str, raise_for_status=True, ssl=self._ssl_verify
            ) as resp:
                image_content = await resp.read()
        except Exception as e:
            logger.exception('Failed to GET %s', query_str)
            await _failure_queue.put(
                ImageRecord(url=query_str, parameters=call_params, error=e)
            )
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
                await _failure_queue.put(
                    ImageRecord(url=query_str, parameters=call_params, error=e)
                )
                return
        else:
            img_data = None

        await _success_queue.put(
            ImageRecord(
                url=query_str, parameters=call_params, name=image_name, content=img_data,
                output_file=out_file
            )
        )

    async def show(self, observation_ids):
        """
        Get attributes for observations.

        Args:
            observation_ids (str or list of strs): Helios observation ID(s).

        Returns:
            tuple: A tuple containing:
                feature_collection (:class:`ObservationsFeatureCollection <helios.observations_api.ObservationsFeatureCollection>`):
                    Observations feature collection.
                failed (list of :class:`Record <helios.core.structure.Record>`):
                    Failed API call records.

        """

        succeeded, failed = super(Observations, self).show(observation_ids)

        content = []
        for record in succeeded:
            content.append(ObservationsFeature(record.content))

        return ObservationsFeatureCollection(content), failed


class ObservationsFeature(object):
    """
    Individual Observation GeoJSON feature.

    Attributes:
        city (str): 'city' value for the feature.
        country (str): 'country' value for the feature.
        description (str): 'description' value for the feature.
        id (str): 'id' value for the feature.
        json (dict): Raw JSON feature.
        prev_id (str): 'prev_id' value for the feature.
        region (str): 'region' value for the feature.
        sensors (dict): 'sensors' value for the feature.
        state (str): 'state' value for the feature.
        time (str): 'time' value for the feature.

    """

    def __init__(self, feature):
        self.json = feature

    @property
    def city(self):
        return self.json['properties'].get('city')

    @property
    def country(self):
        return self.json['properties'].get('country')

    @property
    def description(self):
        return self.json['properties'].get('description')

    @property
    def id(self):
        return self.json.get('id')

    @property
    def prev_id(self):
        return self.json['properties'].get('prev_id')

    @property
    def region(self):
        return self.json['properties'].get('region')

    @property
    def sensors(self):
        return self.json['properties'].get('sensors')

    @property
    def state(self):
        return self.json['properties'].get('state')

    @property
    def time(self):
        return self.json['properties'].get('time')


class ObservationsFeatureCollection(object):
    """
    Collection of GeoJSON features obtained via the Observations API.

    Convenience properties are available to extract values from every feature.

    Attributes:
        features (list of :class:`ObservationsFeature <helios.core.structure.ObservationsFeature>`):
            All features returned from a query.

    """

    def __init__(self, features):
        self.features = features

    @property
    def city(self):
        """'city' values for every feature."""
        return [x.city for x in self.features]

    @property
    def country(self):
        """'country' values for every feature."""
        return [x.country for x in self.features]

    @property
    def description(self):
        """'description' values for every feature."""
        return [x.description for x in self.features]

    @property
    def id(self):
        """'id' values for every feature."""
        return [x.id for x in self.features]

    @property
    def json(self):
        """Raw 'json' for every feature."""
        return [x.json for x in self.features]

    @property
    def prev_id(self):
        """'prev_id' values for every feature."""
        return [x.prev_id for x in self.features]

    @property
    def region(self):
        """'region' values for every feature."""
        return [x.region for x in self.features]

    @property
    def sensors(self):
        """'sensors' values for every feature."""
        return [x.sensors for x in self.features]

    @property
    def state(self):
        """'state' values for every feature."""
        return [x.state for x in self.features]

    @property
    def time(self):
        """'time' values for every feature."""
        return [x.time for x in self.features]

    @property
    def observations(self):
        """
        Observation data from the sensor block of each feature.

        Data will be returned as a dictionary with a key for each sensor.
        Observation data for each sensor is a named tuple ease-of-use.

        Each named tuple contains the sensor, time, data, prev, id, and prev_id.

        """

        Observation = namedtuple(
            'Observation', ['sensor', 'time', 'data', 'prev', 'id', 'prev_id']
        )
        data = defaultdict(list)
        for feature in self.features:
            for sensor, sensor_data in feature.sensors.items():
                data[sensor].append(
                    Observation(
                        sensor,
                        feature.time,
                        sensor_data.get('data', -1),
                        sensor_data.get('prev', -1),
                        feature.id,
                        feature.prev_id,
                    )
                )

        return dict(data)
