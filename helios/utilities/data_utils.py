"""Utilities for working with SDK results."""

from helios.alerts_api import AlertsFeatureCollection
from helios.cameras_api import CamerasFeatureCollection
from helios.collections_api import CollectionsFeatureCollection
from helios.observations_api import ObservationsFeatureCollection


def concatenate_feature_collections(fc_tuple):
    """
    Joins a sequence of FeatureCollections.

    Args:
        fc_tuple (tuple): (fc0, fc1, fc2, ...) FeatureCollections to be
            combined.  All FeatureCollections must be of the same type.

    Returns:
        FeatureCollection: FeatureCollection of the same API type as the input.

    """
    # Check for consistent instance types.
    if not all([isinstance(x, type(fc_tuple[0])) for x in fc_tuple]):
        raise TypeError('FeatureCollection type mismatches found.')

    if isinstance(fc_tuple[0], AlertsFeatureCollection):
        fc_alias = AlertsFeatureCollection
    elif isinstance(fc_tuple[0], CamerasFeatureCollection):
        fc_alias = CamerasFeatureCollection
    elif isinstance(fc_tuple[0], CollectionsFeatureCollection):
        fc_alias = CollectionsFeatureCollection
    elif isinstance(fc_tuple[0], ObservationsFeatureCollection):
        fc_alias = ObservationsFeatureCollection
    else:
        raise TypeError('Feature collection of unknown type.')

    # Gather all features and records from each feature collection.
    features = []
    records = []
    for fc in fc_tuple:
        features.extend(fc.features)
        records.extend(fc.records._records)

    return fc_alias(features, records=records)
