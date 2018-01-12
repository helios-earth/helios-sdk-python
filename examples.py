"""Usage Examples."""
import argparse
import os

from heliosSDK import Cameras, Collections, Observations, Alerts
from heliosSDK.utilities import json_utils


def test_alerts(output_dir=''):
    """Alerts Core API Testing."""
    alerts = Alerts()

    alerts_test_0 = alerts.index(country='United States')
    json_utils.write_json(alerts_test_0,
                          os.path.join(output_dir, r'alerts_index.json'))

    example_id = alerts_test_0[0]['features'][0]['id']

    alerts_test_1 = alerts.show(example_id)
    json_utils.write_json(alerts_test_1,
                          os.path.join(output_dir, r'alerts_show.json'))


def test_cameras(output_dir=''):
    """Cameras Core API Testing."""
    cameras = Cameras()

    cameras_test_0 = cameras.index(aggs='city', state='New York')
    json_utils.write_json(cameras_test_0,
                          os.path.join(output_dir, r'cameras_index.json'))
    cam_id = cameras_test_0[0]['features'][0]['id']

    cameras_test_1 = cameras.show(cam_id)
    json_utils.write_json(cameras_test_1,
                          os.path.join(output_dir, r'cameras_show.json'))

    cameras_test_2 = cameras.images(cam_id,
                                    '2017-01-02T15:00:00.000Z', limit=10)
    json_utils.write_json(cameras_test_2,
                          os.path.join(output_dir, r'cameras_images.json'))

    cameras_test_3 = cameras.show_image(cam_id, cameras_test_2)
    json_utils.write_json(cameras_test_3,
                          os.path.join(output_dir, r'cameras_showImages.json'))

    cameras_test_4 = cameras.download_images(
        cameras_test_3,
        out_dir=os.path.join(output_dir, r'Images'),
        return_image_data=True)


def test_observations(output_dir=''):
    """Observations Core API Testing."""
    observations = Observations()

    observations_test_0 = observations.index(
        aggs='city', bbox='-77.564,42.741,-76.584,43.193')
    json_utils.write_json(observations_test_0,
                          os.path.join(output_dir, r'observations_index.json'))

    # Extract id from index query
    for feature in observations_test_0[0]['features']:
        temp_id = feature['id']
        try:
            temp_id.index('error')
        except ValueError:
            break

    observations_test_1 = observations.show(temp_id)
    json_utils.write_json(observations_test_1,
                          os.path.join(output_dir, r'observations_show.json'))

    observations_test_2 = observations.preview(temp_id)
    json_utils.write_json(observations_test_2,
                          os.path.join(output_dir,
                                       r'observations_preview.json'))

    observations_test_3 = observations.download_images(
        observations_test_2,
        out_dir=os.path.join(output_dir, r'Images_Observation'),
        return_image_data=True)


def test_collections(output_dir=''):
    """Collections Core API Testing."""
    collections = Collections()

    collections_test_0 = collections.index(q='raindrops')
    json_utils.write_json(collections_test_0,
                          os.path.join(output_dir, r'collections_index.json'))

    collections_test_1 = collections.show(
        '6a59fd46-bdf0-47e4-a719-992a9e9e988b')
    json_utils.write_json(collections_test_1,
                          os.path.join(output_dir, r'collections_show.json'))

    collections_test_2 = collections.show(
        '6a59fd46-bdf0-47e4-a719-992a9e9e988b', marker='d458-VADOT-86619')
    json_utils.write_json(collections_test_2,
                          os.path.join(output_dir,
                                       r'collections_show_VADOT-86619.json'))

    collections_test_3 = collections.images(
        '6a59fd46-bdf0-47e4-a719-992a9e9e988b')
    json_utils.write_json(collections_test_3,
                          os.path.join(output_dir, r'collections_images.json'))

    collections_test_4 = collections.show_image(
        '6a59fd46-bdf0-47e4-a719-992a9e9e988b',
        collections_test_3[0])
    json_utils.write_json(collections_test_4,
                          os.path.join(output_dir,
                                       r'collections_showImage.json'))

    collections_test_5 = collections.show_image(
        '6a59fd46-bdf0-47e4-a719-992a9e9e988b', collections_test_3)
    json_utils.write_json(collections_test_5,
                          os.path.join(output_dir,
                                       r'collections_showImages.json'))

    collections_test6 = collections.download_images(
        collections_test_5,
        out_dir=os.path.join(output_dir, r'Images_Collection'),
        return_image_data=True)


def main():
    """Run example queries."""
    parser = argparse.ArgumentParser(
        description='Wrapper for Annotation Detection.',
        formatter_class=argparse.RawTextHelpFormatter)
    required = parser.add_argument_group('Required arguments:')
    required.add_argument('-o',
                          help='Output directory for test results.',
                          required=True,
                          type=str)
    args = parser.parse_args()

    print('Alerts testing...')
    test_alerts(args.o)
    print('Cameras testing...')
    test_cameras(args.o)
    print('Observations testing...')
    test_observations(args.o)
    print('Collections testing...')
    test_collections(args.o)
    print('COMPLETE')


if __name__ == '__main__':
    main()
