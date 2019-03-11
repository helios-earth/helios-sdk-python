import pytest

from helios import collections_api


def test_collections_features(collections_json):
    collections_feature = collections_api.CollectionsFeature(collections_json)
    collections_fc = collections_api.CollectionsFeatureCollection(
        [collections_feature, collections_feature])
    assert len(collections_fc.features) == 2


if __name__ == '__main__':
    pytest.main([__file__])
