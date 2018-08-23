import pytest

import helios
from helios.core.structure import Record


@pytest.fixture(scope='session')
def record():
    return Record(message=('test',), query='test', content='test', error=None)


@pytest.fixture(scope='session')
def record_fail():
    return Record(message=('test',), query='test', content='test',
                  error=Exception('test'))


@pytest.fixture(scope='session')
def alerts_json():
    data = {'type': 'Feature',
            'id': 'LA1258631A7ED0.TornadoWarning.1258631A9AF0LA.LIXTORLIX.17da17441c9808bc0e5d397f3e2779b0',
            'bbox': [-90.29, 29.09, -90.12, 29.37],
            'geometry': {
                'type': 'Polygon',
                'coordinates': []
            },
            'properties': {
                'origin': 'NWS',
                'event': 'Tornado Warning',
                'headline': 'Tornado Warning issued August 29 at 5:28AM CDT until August 29 at 6:00AM CDT by NWS',
                'states': ['Louisiana'],
                'areaDesc': 'Lafourche',
                'description': '..',
                'effective': '2017-08-29T10:28:00.000Z',
                'expires': '2017-08-29T11:00:00.000Z',
                'updated': '2017-08-29T10:28:00.000Z',
                'urgency': 'Immediate',
                'severity': 'Extreme',
                'certainty': 'Observed',
                'status': 'Actual',
                'tracking_line': {
                    'time': '1027Z',
                    'azimuth': 170,
                    'velocity': 25,
                    'geometry': {
                        'type': 'LineString',
                        'coordinates': [[-90.18, 29.16], [-90.18, 29.16]]}}}}
    return data


@pytest.fixture(scope='session')
def cameras_json():
    data = {'type': 'Feature',
            'id': 'VADOT-85975',
            'geometry': {
                'type': 'Point',
                'coordinates': [-76.19457, 36.82146]
            },
            'properties': {
                'country': 'United States',
                'state': 'Virginia',
                'city': 'Virginia Beach',
                'provider': 'VA DOT',
                'description': 'I-64 / MM 285 / WB / OL TWIN BRIDGES & PROVIDENCE',
                'video': True}}
    return data


@pytest.fixture(scope='session')
def collections_json():
    data = {'_id': 'my-collection',
            'name': 'My collection',
            'description': 'My favorite images',
            'tags': ['foo', 'bar'],
            'created_at': '2016-08-01T12:34:56.789Z',
            'updated_at': '2016-08-01T12:34:56.789Z'}
    return data


@pytest.fixture(scope='session')
def observations_json():
    data = {'type': 'Feature',
            'id': 'CADOT-807986_2017-07-21T22:10:00.000Z',
            'geometry': {
                'coordinates': [-117.4887542724609, 34.14170455932617],
                'type': 'Point'
            },
            'properties': {
                'camera_id': 'CADOT-807986',
                'prev_id': 'CADOT-807986_2017-07-21T22:00:00.000Z',
                'description': 'Cherry Avenue',
                'city': 'Fontana',
                'state': 'California',
                'country': 'United States',
                'time': '2017-07-21T22:10:00.000Z',
                'sensors': {'visibility': {'data': 1},
                            'road_weather': {'data': 3, 'prev': 0}}}}
    return data


@pytest.fixture(scope='session')
def alerts_feature_collection(alerts_json, record, record_fail):
    alerts_feature = helios.alerts_api.AlertsFeature(alerts_json)
    alerts_fc = helios.alerts_api.AlertsFeatureCollection(
        [alerts_feature, alerts_feature],
        records=[record, record_fail])

    return alerts_fc


@pytest.fixture(scope='session')
def cameras_feature_collection(cameras_json, record, record_fail):
    cameras_feature = helios.cameras_api.CamerasFeature(cameras_json)
    cameras_fc = helios.cameras_api.CamerasFeatureCollection(
        [cameras_feature, cameras_feature],
        records=[record, record_fail])

    return cameras_fc


@pytest.fixture(scope='session')
def collections_feature_collection(collections_json, record, record_fail):
    collections_feature = helios.collections_api.CollectionsFeature(collections_json)
    collections_fc = helios.collections_api.CollectionsFeatureCollection(
        [collections_feature, collections_feature],
        records=[record, record_fail])

    return collections_fc


@pytest.fixture(scope='session')
def observations_feature_collection(observations_json, record, record_fail):
    observations_feature = helios.observations_api.ObservationsFeature(observations_json)
    observations_fc = helios.observations_api.ObservationsFeatureCollection(
        [observations_feature, observations_feature],
        records=[record, record_fail])

    return observations_fc
