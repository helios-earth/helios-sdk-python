import pytest

from helios import cameras_api


def test_alerts_features(cameras_json):
    cameras_feature = cameras_api.CamerasFeature(cameras_json)
    cameras_fc = cameras_api.CamerasFeatureCollection([cameras_feature, cameras_feature])
    assert len(cameras_fc.features) == 2


if __name__ == '__main__':
    pytest.main([__file__])
