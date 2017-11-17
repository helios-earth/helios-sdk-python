'''
Usage Examples

@author: Michael A. Bayer
'''
import argparse
import os

from heliosSDK import Cameras, Collections, Observations, Alerts
from heliosSDK.utilities import jsonTools


def testAlerts(output_dir=''):
    """
    Alerts Core API Testing
    """
    AC = Alerts()

    alerts_test_0 = AC.index(country='United States')
    jsonTools.writeJson(alerts_test_0, os.path.join(output_dir, r'alerts_index.json'))

    example_id = alerts_test_0[0]['features'][0]['id']

    alerts_test_1 = AC.show(example_id)
    jsonTools.writeJson(alerts_test_1, os.path.join(output_dir, r'alerts_show.json'))


def testCameras(output_dir=''):
    """
    Cameras Core API Testing
    """
    CaC = Cameras()

    cameras_test_0 = CaC.index(aggs='city', state='New York')
    jsonTools.writeJson(cameras_test_0, os.path.join(output_dir, r'cameras_index.json'))
    cam_id = cameras_test_0[0]['features'][0]['id']

    cameras_test_1 = CaC.show(cam_id)
    jsonTools.writeJson(cameras_test_1, os.path.join(output_dir, r'cameras_show.json'))

    cameras_test_2 = CaC.images(cam_id, '2017-01-02T15:00:00.000Z', limit=10)
    jsonTools.writeJson(cameras_test_2, os.path.join(output_dir, r'cameras_images.json'))

    cameras_test_3 = CaC.showImage(cam_id, cameras_test_2['times'])
    jsonTools.writeJson(cameras_test_3, os.path.join(output_dir, r'cameras_showImages.json'))

    cameras_test_4 = CaC.downloadImages(cameras_test_3['url'], out_dir=os.path.join(output_dir, r'Images'),
                                        return_image_data=True)


def testObservations(output_dir=''):
    """
    Observations Core API Testing
    """
    OC = Observations()

    observations_test_0 = OC.index(aggs='city', bbox='-77.564,42.741,-76.584,43.193')
    jsonTools.writeJson(observations_test_0, os.path.join(output_dir, r'observations_index.json'))

    temp_id = observations_test_0[0]['features'][0]['id']

    observations_test_1 = OC.show(temp_id)
    jsonTools.writeJson(observations_test_1, os.path.join(output_dir, r'observations_show.json'))

    observations_test_2 = OC.preview(temp_id)
    jsonTools.writeJson(observations_test_2['url'], os.path.join(output_dir, r'observations_preview.json'))

    observations_test_3 = OC.downloadImages(observations_test_2['url'],
                                            out_dir=os.path.join(output_dir, r'Images_Observation'),
                                            return_image_data=True)


def testCollections(output_dir=''):
    """
    Collections Core API Testing
    """

    CC = Collections()

    collections_test_0 = CC.index(q='raindrops')
    jsonTools.writeJson(collections_test_0, os.path.join(output_dir, r'collections_index.json'))

    collections_test_1 = CC.show('6a59fd46-bdf0-47e4-a719-992a9e9e988b')
    jsonTools.writeJson(collections_test_1, os.path.join(output_dir, r'collections_show.json'))

    collections_test_2 = CC.show('6a59fd46-bdf0-47e4-a719-992a9e9e988b', marker='d458-VADOT-86619')
    jsonTools.writeJson(collections_test_2, os.path.join(output_dir, r'collections_show_VADOT-86619.json'))

    # output = Collections2.create('test_collection_new', description='test', ['test','test2','test3'])

    collections_test_3 = CC.images('6a59fd46-bdf0-47e4-a719-992a9e9e988b')
    jsonTools.writeJson(collections_test_3, os.path.join(output_dir, r'collections_images.json'))

    collections_test_4 = CC.showImage('6a59fd46-bdf0-47e4-a719-992a9e9e988b', collections_test_3['images'][0])
    jsonTools.writeJson(collections_test_4, os.path.join(output_dir, r'collections_showImage.json'))

    collections_test_5 = CC.showImage('6a59fd46-bdf0-47e4-a719-992a9e9e988b', collections_test_3['images'])
    jsonTools.writeJson(collections_test_5, os.path.join(output_dir, r'collections_showImages.json'))

    collections_test6 = CC.downloadImages(collections_test_5['url'],
                                          out_dir=os.path.join(output_dir, r'Images_Collection'),
                                          return_image_data=True)

    # output = Collections2.copy('d860fa88-a55d-4edb-b769-e1a0b5f3ad01', 'test_collection')


def main():
    parser = argparse.ArgumentParser(description='Wrapper for Annotation Detection.',
                                     formatter_class=argparse.RawTextHelpFormatter)
    required = parser.add_argument_group('Required arguments:')
    required.add_argument('-o', help='Output directory for test results.', required=True, type=str)
    args = parser.parse_args()

    print('Alerts testing...')
    testAlerts(args.o)
    print('Cameras testing...')
    testCameras(args.o)
    print('Observations testing...')
    testObservations(args.o)
    print('Collections testing...')
    testCollections(args.o)
    print('COMPLETE')


if __name__ == '__main__':
    main()
