import pytest

from helios.utilities import data_utils


def test_concatenate_feature_collections(alerts_feature_collection,
                                         cameras_feature_collection,
                                         collections_feature_collection,
                                         observations_feature_collection):
    alerts_combined = data_utils.concatenate_feature_collections(
        alerts_feature_collection, alerts_feature_collection)
    assert len(alerts_combined.features) == 4

    cameras_combined = data_utils.concatenate_feature_collections(
        cameras_feature_collection, cameras_feature_collection)
    assert len(cameras_combined.features) == 4

    collections_combined = data_utils.concatenate_feature_collections(
        collections_feature_collection, collections_feature_collection)
    assert len(collections_combined.features) == 4

    observations_combined = data_utils.concatenate_feature_collections(
        observations_feature_collection, observations_feature_collection)
    assert len(observations_combined.features) == 4


if __name__ == '__main__':
    pytest.main([__file__])
