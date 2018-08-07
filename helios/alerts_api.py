"""
Helios Alerts API.

Methods are meant to represent the core functionality in the developer
documentation.  Some may have additional functionality for convenience.

"""
import logging

from helios.core.mixins import SDKCore, IndexMixin, ShowMixin
from helios.core.structure import RecordCollection

logger = logging.getLogger(__name__)


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

    def index(self, **kwargs):
        """
        Get alerts matching the provided spatial, text, or
        metadata filters.

        The maximum skip value is 4000. If this is reached, truncated results
        will be returned. You will need to refine your query to avoid this.

        .. _alerts_index_documentation: https://helios.earth/developers/api/alerts/#index

        Args:
            **kwargs: Any keyword arguments found in the alerts_index_documentation_.

        Returns:
             :class:`AlertsFeatureCollection <helios.alerts_api.AlertsFeatureCollection>`

        """
        results = super(Alerts, self).index(**kwargs)

        content = []
        for record in results:
            if record.ok:
                for feature in record.content['features']:
                    content.append(AlertsFeature(feature))

        return AlertsFeatureCollection(content, results)

    def show(self, alert_ids):
        """
        Get attributes for alerts.

        Args:
            alert_ids (str or sequence of strs): Helios alert ID(s).

        Returns:
            :class:`AlertsFeatureCollection <helios.alerts_api.AlertsFeatureCollection>`

        """
        results = super(Alerts, self).show(alert_ids)

        content = []
        for record in results:
            if record.ok:
                content.append(AlertsFeature(record.content))

        return AlertsFeatureCollection(content, results)


class AlertsFeature(object):
    """
    Individual Alert GeoJSON feature.

    Attributes:
        area_description (str): 'areaDesc' value for the feature.
        bbox (sequence of floats): 'bbox' value for the feature.
        category (str): 'category' value for the feature.
        certainty (str): 'certainty' value for the feature.
        country (str): 'country' value for the feature.
        description (str): 'description' value for the feature.
        effective (str): 'effective' value for the feature.
        event (str): 'event' value for the feature.
        expires (str): 'expires' value for the feature.
        headline (str): 'headline' value for the feature.
        id (str): 'id' value for the feature.
        json (dict): Raw 'json' for the feature.
        origin (str): 'origin' value for the feature.
        severity (str): 'severity' value for the feature.
        states (sequence of strs): 'states' value for the feature.
        status (str): 'status' value for the feature.
        urgency (str): 'urgency' value for the feature.

    """

    def __init__(self, feature):
        self.json = feature

        # Use dict.get built-in to guarantee all values will be initialized.
        self.area_description = feature['properties'].get('areaDesc')
        self.bbox = feature.get('bbox')
        self.category = feature['properties'].get('category')
        self.certainty = feature['properties'].get('certainty')
        self.country = feature['properties'].get('country')
        self.description = feature['properties'].get('description')
        self.effective = feature['properties'].get('effective')
        self.event = feature['properties'].get('event')
        self.expires = feature['properties'].get('expires')
        self.headline = feature['properties'].get('headline')
        self.id = feature.get('id')
        self.origin = feature['properties'].get('origin')
        self.severity = feature['properties'].get('severity')
        self.states = feature['properties'].get('states')
        self.status = feature['properties'].get('status')
        self.urgency = feature['properties'].get('urgency')


class AlertsFeatureCollection(RecordCollection):
    """
    Collection of GeoJSON features obtained via the Alerts API.

    Convenience properties are available to extract values from every feature.

    Attributes:
        features (list of :class:`AlertsFeature <helios.alerts_api.AlertsFeature>`):
            All features returned from a query.

    """

    def __init__(self, features, records):
        super(AlertsFeatureCollection, self).__init__(records)
        self.features = features

    @property
    def area_description(self):
        """'areaDesc' values for every feature."""
        return [x.area_description for x in self.features]

    @property
    def bbox(self):
        """'bbox' values for every feature."""
        return [x.bbox for x in self.features]

    @property
    def category(self):
        """'category' values for every feature."""
        return [x['properties']['category'] for x in self.features]

    @property
    def certainty(self):
        """'certainty' values for every feature."""
        return [x.certainty for x in self.features]

    @property
    def country(self):
        """'country' values for every feature."""
        return [x.country for x in self.features]

    @property
    def description(self):
        """'description' values for every feature."""
        return [x.description for x in self.features]

    @property
    def effective(self):
        """'effective' values for every feature."""
        return [x.effective for x in self.features]

    @property
    def event(self):
        """'event' values for every feature."""
        return [x.event for x in self.features]

    @property
    def expires(self):
        """'expires' values for every feature."""
        return [x.expires for x in self.features]

    @property
    def headline(self):
        """'headline' values for every feature."""
        return [x.headline for x in self.features]

    @property
    def id(self):
        """'id' values for every feature."""
        return [x.id for x in self.features]

    @property
    def json(self):
        """Raw 'json' for every feature."""
        return [x.json for x in self.features]

    @property
    def origin(self):
        """'origin' values for every feature."""
        return [x.origin for x in self.features]

    @property
    def severity(self):
        """'severity' values for every feature."""
        return [x.severity for x in self.features]

    @property
    def states(self):
        """'states' values for every feature."""
        return [x.states for x in self.features]

    @property
    def status(self):
        """'status' values for every feature."""
        return [x.status for x in self.features]

    @property
    def urgency(self):
        """'urgency' values for every feature."""
        return [x.urgency for x in self.features]
