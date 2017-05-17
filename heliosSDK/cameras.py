'''
SDK for the Helios Cameras API.  Methods are meant to represent the core
functionality in the developer documentation.  Some may have additional
functionality for convenience.  

@author: Michael A. Bayer
'''
from heliosSDK.core import SDKCore, ShowMixin, ShowImageMixin, IndexMixin, DownloadImagesMixin
from heliosSDK.utilities import jsonTools

from dateutil.parser import parse
from pathos.multiprocessing import freeze_support, ProcessingPool, cpu_count


class Cameras(DownloadImagesMixin, ShowImageMixin, ShowMixin, IndexMixin, SDKCore):
    _CORE_API = 'cameras'
    
    def __init__(self):
        self._startSession()
        
    def index(self, **kwargs):
        return super(Cameras, self).index(**kwargs)
    
    def show(self, camera_id):
        return super(Cameras, self).show(camera_id)
    
    def images(self, camera_id, start_time, limit=500):
        query_str = '{}/{}/{}/images?time={}&limit={}'.format(self._BASE_API_URL,
                                                              self._CORE_API,
                                                              camera_id,
                                                              start_time,
                                                              limit)
        resp = self._getRequest(query_str,
                               headers={self._AUTH_TOKEN['name']:self._AUTH_TOKEN['value']},
                               verify=self._SSL_VERIFY) 
        json_response = resp.json()
        
        return json_response

    def imagesRange(self, camera_id, start_time, end_time, limit=500):             
        end_time = parse(end_time) 
        output_json = []
        count = 0
        while True:
            json_response = self.images(camera_id,
                                        start_time,
                                        limit=limit)
            
            times = json_response['times']
            n = json_response['total']
            count += n
                        
            if json_response['total'] == 0:
                break
                
            first = parse(times[0])
            last = parse(times[-1])
            
            if first > end_time:
                break
            
            if len(times) == 1:
                output_json.extend(times)
                break
                
            # the last image is still newer than our end time, keep looking    
            if last < end_time:
                output_json.extend(times)
                start_time = times[-1]
                continue
            else:
                good_times = [x for x in times if parse(x) < end_time]
                output_json.extend(good_times)
                break

        return {'total':len(output_json), 'times':output_json}
    
    def showImage(self, camera_id, time, delta=900000):
        return super(Cameras, self).showImage(camera_id, time, delta=delta)
    
    def showImages(self, camera_id, start_time, end_time, limit=500):
            results = self.imagesRange(camera_id, start_time, end_time, limit=limit)
            times = results['times']
            
            n_p = max([1, int(cpu_count() / 2)])
            if n_p > 1 and len(times) > 10:
                pool = ProcessingPool(n_p)
                results2 = pool.map(self.showImage, [camera_id] * len(times), times)
            else:
                results2 = [self.showImage(camera_id, time) for time in times]
            urls = jsonTools.mergeJson(results2, 'url')
            
            json_output = {'url':urls}
                
            return json_output
        
    def downloadImages(self, urls, out_dir=None, return_image_data=False):
        return super(Cameras, self).downloadImages(urls, out_dir=out_dir, return_image_data=return_image_data)
    
if __name__ == '__main__':
    freeze_support()
