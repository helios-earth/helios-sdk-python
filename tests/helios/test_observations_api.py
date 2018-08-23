import pytest

from helios import observations_api


def test_observations_features(observations_json, record, record_fail):
    observations_feature = observations_api.ObservationsFeature(observations_json)
    observations_fc = observations_api.ObservationsFeatureCollection(
        [observations_feature, observations_feature],
        records=[record, record_fail])
    assert len(observations_fc.features) == 2
    assert len(observations_fc.records.failed) == 1
    assert len(observations_fc.records.succeeded) == 1


if __name__ == '__main__':
    pytest.main([__file__])
