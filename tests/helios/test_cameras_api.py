import pytest

from helios import cameras_api


def test_alerts_features(cameras_json, record, record_fail):
    cameras_feature = cameras_api.CamerasFeature(cameras_json)
    cameras_fc = cameras_api.CamerasFeatureCollection([cameras_feature, cameras_feature],
                                                      records=[record, record_fail])
    assert len(cameras_fc.features) == 2
    assert len(cameras_fc.records.failed) == 1
    assert len(cameras_fc.records.succeeded) == 1


if __name__ == '__main__':
    pytest.main([__file__])
