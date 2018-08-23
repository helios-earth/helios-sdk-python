import pytest

from helios import collections_api


def test_collections_features(collections_json, record, record_fail):
    collections_feature = collections_api.CollectionsFeature(collections_json)
    collections_fc = collections_api.CollectionsFeatureCollection(
        [collections_feature, collections_feature],
        records=[record, record_fail])
    assert len(collections_fc.features) == 2
    assert len(collections_fc.records.failed) == 1
    assert len(collections_fc.records.succeeded) == 1


if __name__ == '__main__':
    pytest.main([__file__])
