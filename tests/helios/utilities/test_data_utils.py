import pytest

from helios.utilities import data_utils


def test_concatenate_feature_collections(alerts_feature_collection,
                                         cameras_feature_collection,
                                         collections_feature_collection,
                                         observations_feature_collection):
    alerts_combined = data_utils.concatenate_feature_collections(
        (alerts_feature_collection, alerts_feature_collection))
    assert len(alerts_combined.features) == 4
    assert len(alerts_combined.records.failed) == 2
    assert len(alerts_combined.records.succeeded) == 2

    cameras_combined = data_utils.concatenate_feature_collections(
        (cameras_feature_collection, cameras_feature_collection))
    assert len(cameras_combined.features) == 4
    assert len(cameras_combined.records.failed) == 2
    assert len(cameras_combined.records.succeeded) == 2

    collections_combined = data_utils.concatenate_feature_collections(
        (collections_feature_collection, collections_feature_collection))
    assert len(collections_combined.features) == 4
    assert len(collections_combined.records.failed) == 2
    assert len(collections_combined.records.succeeded) == 2

    observations_combined = data_utils.concatenate_feature_collections(
        (observations_feature_collection, observations_feature_collection))
    assert len(observations_combined.features) == 4
    assert len(observations_combined.records.failed) == 2
    assert len(observations_combined.records.succeeded) == 2


if __name__ == '__main__':
    pytest.main([__file__])
