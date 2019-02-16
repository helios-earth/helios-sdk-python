import pytest

from helios import observations_api


def test_observations_features(observations_json, record, record_fail):
    observations_feature = observations_api.ObservationsFeature(observations_json)
    observations_fc = observations_api.ObservationsFeatureCollection(
        [observations_feature, observations_feature])
    assert len(observations_fc.features) == 2


if __name__ == '__main__':
    pytest.main([__file__])
