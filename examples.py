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
    Alerts2 = Alerts()
      
    alerts_test_0 = Alerts2.index(state='Louisiana')
    jsonTools.writeJson(alerts_test_0, os.path.join(output_dir, r'alerts_index.json'))
    
    example_id = alerts_test_0[0]['features'][0]['id']
    alerts_test_1 = Alerts2.show(example_id)
    jsonTools.writeJson(alerts_test_1, os.path.join(output_dir, r'alerts_show.json'))
    
def testCameras(output_dir=''):
    """
    Cameras Core API Testing
    """
    Cameras2 = Cameras()
    
    cameras_test_0 = Cameras2.index(aggs='city', state='New York')
    jsonTools.writeJson(cameras_test_0, os.path.join(output_dir, r'cameras_index.json'))
       
    cameras_test_1 = Cameras2.show('TL-403389')
    jsonTools.writeJson(cameras_test_1, os.path.join(output_dir, r'cameras_show.json'))
       
    cameras_test_2 = Cameras2.imagesRange('TL-6140', '2017-01-02T15:00:00.000Z', '2017-01-02T16:00:00.000Z')
    jsonTools.writeJson(cameras_test_2, os.path.join(output_dir, r'cameras_images.json'))
           
    cameras_test_3 = Cameras2.showImages('TL-6140', '2017-01-02T15:00:00.000Z', '2017-01-02T16:00:00.000Z')
    jsonTools.writeJson(cameras_test_3, os.path.join(output_dir, r'cameras_showImages.json'))
    
    cameras_test_4 = Cameras2.downloadImages(cameras_test_3['url'], out_dir=os.path.join(output_dir, r'Images'), return_image_data=True)
      
def testObservations(output_dir=''):
    """
    Observations Core API Testing
    """
    Observations2 = Observations()
    
    observations_test_0 = Observations2.index(aggs='city', bbox='-77.564,42.741,-76.584,43.193')
    jsonTools.writeJson(observations_test_0, os.path.join(output_dir, r'observations_index.json'))
    
    observations_test_1 = Observations2.show('TL-6532_2017-03-27T12:15:00.000Z')
    jsonTools.writeJson(observations_test_1, os.path.join(output_dir, r'observations_show.json'))
    
    temp_id = observations_test_0[0]['features'][0]['id']
    observations_test_2 = Observations2.preview(temp_id)
    jsonTools.writeJson(observations_test_2['url'], os.path.join(output_dir, r'observations_preview.json'))
    
    observations_test_3 = Observations2.downloadImages(observations_test_2['url'], out_dir=os.path.join(output_dir, r'Images_Observation'), return_image_data=True)

def testCollections(output_dir=''):
    """
    Collections Core API Testing
    """
     
    Collections2 = Collections()
     
    collections_test_0 = Collections2.index(q='raindrops')
    jsonTools.writeJson(collections_test_0, os.path.join(output_dir, r'collections_index.json'))
      
    collections_test_1 = Collections2.show('6a59fd46-bdf0-47e4-a719-992a9e9e988b')
    jsonTools.writeJson(collections_test_1, os.path.join(output_dir, r'collections_show.json'))
        
    collections_test_2 = Collections2.show('6a59fd46-bdf0-47e4-a719-992a9e9e988b', marker='d458-VADOT-86619')
    jsonTools.writeJson(collections_test_2, os.path.join(output_dir, r'collections_show_VADOT-86619.json'))
        
    # output = Collections2.create('test_collection_new', description='test', ['test','test2','test3'])
     
    collections_test_3 = Collections2.images('6a59fd46-bdf0-47e4-a719-992a9e9e988b', 'VADOT-86619', old_flag=False)
    jsonTools.writeJson(collections_test_3, os.path.join(output_dir, r'collections_images.json'))
     
    collections_test_4 = Collections2.showImage('6a59fd46-bdf0-47e4-a719-992a9e9e988b', 'c7ee-TL-5320_20160407133435000.jpg')
    jsonTools.writeJson(collections_test_4, os.path.join(output_dir, r'collections_showImage.json'))
       
    collections_test_5 = Collections2.showImages('6a59fd46-bdf0-47e4-a719-992a9e9e988b', 'VADOT-86619', old_flag=False)
    jsonTools.writeJson(collections_test_5, os.path.join(output_dir, r'collections_showImages.json'))
       
    collections_test6 = Collections2.downloadImages(collections_test_5['url'], out_dir=os.path.join(output_dir, r'Images_Collection'), return_image_data=True)
             
    # output = Collections2.copy('d860fa88-a55d-4edb-b769-e1a0b5f3ad01', 'test_collection')
    
def main():
    parser = argparse.ArgumentParser(description='Wrapper for Annotation Detection.', formatter_class=argparse.RawTextHelpFormatter)
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
