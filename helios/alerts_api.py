"""
Helios Alerts API.

Methods are meant to represent the core functionality in the developer
documentation.  Some may have additional functionality for convenience.

"""
import logging

from helios.core.mixins import SDKCore, IndexMixin, ShowMixin
from helios.utilities.json_utils import merge_json


class Alerts(ShowMixin, IndexMixin, SDKCore):
    """
    Helios alerts provide real-time severe weather alerts.

    **National Weather Service:**

    - Severe weather alerts for the United States are provided by the
      National Weather Service. These alerts cover events such as Flood
      Warnings, Severe Thunderstorm Warnings, and Special Weather Statements.

    **Helios:**

    - Alerts generated by Helios are based on the sensor measurements from
      the Observations API. These alerts represent regional areas with a high
      detection confidence and currently include: Road Wetness Watch, Poor
      Visibility Watch, and Heavy Precip Watch.

    """

    _core_api = 'alerts'

    def __init__(self, session=None):
        """
        Initialize Alerts instance.

        Args:
            session (helios.Session object, optional): An instance of the
                Session. Defaults to None. If unused a session will be
                created for you.

        """
        super(Alerts, self).__init__(session=session)
        self._logger = logging.getLogger(__name__)

    def index(self, **kwargs):
        """
        Get a list of alerts matching the provided spatial, text, or
        metadata filters.

        The maximum skip value is 4000. If this is reached, truncated results
        will be returned. You will need to refine your query to avoid this.

        .. _alerts_index_documentation: https://helios.earth/developers/api/alerts/#index

        Args:
            **kwargs: Any keyword arguments found in the alerts_index_documentation_.

        Returns:
             list: GeoJSON feature collections.

        """
        return AlertsIndex(super(Alerts, self).index(**kwargs))

    def show(self, alert_ids):
        """
        Get attributes for alerts.

        Args:
            alert_ids (str or sequence of strs): Helios alert ID(s).

        Returns:
            :class:`DataContainer <helios.core.records.DataContainer>`:
            Container of :class:`Record <helios.core.records.Record>` instances.

        """
        return super(Alerts, self).show(alert_ids)


class AlertsIndex(object):
    """Index results for the Alerts API."""

    def __init__(self, geojson):
        self.raw = geojson

        self.id = None
        self.bbox = None
        self.area_description = None
        self.category = None
        self.certainty = None
        self.country = None
        self.description = None
        self.effective = None
        self.event = None
        self.expires = None
        self.headline = None
        self.origin = None
        self.severity = None
        self.states = None
        self.status = None
        self.urgency = None

        self._build()

    def _build(self):
        self.features = []
        for x in self.raw:
            self.features.extend(x['features'])

        self.id = merge_json(self.features, 'id')
        self.bbox = merge_json(self.features, 'bbox')
        self.area_description = merge_json(self.features, ['properties', 'areaDesc'])
        self.category = merge_json(self.features, ['properties', 'category'])
        self.certainty = merge_json(self.features, ['properties', 'certainty'])
        self.country = merge_json(self.features, ['properties', 'country'])
        self.description = merge_json(self.features, ['properties', 'description'])
        self.effective = merge_json(self.features, ['properties', 'effective'])
        self.event = merge_json(self.features, ['properties', 'event'])
        self.expires = merge_json(self.features, ['properties', 'expires'])
        self.headline = merge_json(self.features, ['properties', 'headline'])
        self.origin = merge_json(self.features, ['properties', 'origin'])
        self.severity = merge_json(self.features, ['properties', 'severity'])
        self.states = merge_json(self.features, ['properties', 'states'])
        self.status = merge_json(self.features, ['properties', 'status'])
        self.urgency = merge_json(self.features, ['properties', 'urgency'])
