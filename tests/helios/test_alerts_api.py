import pytest

from helios import alerts_api


def test_alerts_features(alerts_json, record, record_fail):
    alerts_feature = alerts_api.AlertsFeature(alerts_json)
    alerts_fc = alerts_api.AlertsFeatureCollection([alerts_feature, alerts_feature],
                                                   records=[record, record_fail])
    assert len(alerts_fc.features) == 2
    assert len(alerts_fc.records.failed) == 1
    assert len(alerts_fc.records.succeeded) == 1


if __name__ == '__main__':
    pytest.main([__file__])
