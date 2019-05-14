"""Utilities for working with SDK results."""
from helios.alerts_api import AlertsFeatureCollection
from helios.cameras_api import CamerasFeatureCollection
from helios.collections_api import CollectionsFeatureCollection
from helios.observations_api import ObservationsFeatureCollection


def concatenate_feature_collections(*args):
    """
    Concatenates FeatureCollections.

    .. code-block:: python

        import helios
        from helios.utilities.data_utils import concatenate_feature_collections

        cameras = helios.client('cameras')
        results1, failed = cameras.index(state='new york')
        results2, failed = cameras.index(state='maryland')
        combined = concatenate_feature_collections((results1, results2))

    Args:
        args: (fc0, fc1, fc2, ...) FeatureCollections to be
            combined.  All FeatureCollections must be of the same type.

    Returns:
        FeatureCollection: FeatureCollection of the same API type as the input.

    """
    # Check for consistent instance types.
    if not all([isinstance(x, type(args[0])) for x in args]):
        raise TypeError('FeatureCollection type mismatches found.')

    if isinstance(args[0], AlertsFeatureCollection):
        fc_alias = AlertsFeatureCollection
    elif isinstance(args[0], CamerasFeatureCollection):
        fc_alias = CamerasFeatureCollection
    elif isinstance(args[0], CollectionsFeatureCollection):
        fc_alias = CollectionsFeatureCollection
    elif isinstance(args[0], ObservationsFeatureCollection):
        fc_alias = ObservationsFeatureCollection
    else:
        raise TypeError('Feature collection of unknown type.')

    # Gather all features and records from each feature collection.
    features = []
    for fc in args:
        features.extend(fc.features)

    return fc_alias(features)
