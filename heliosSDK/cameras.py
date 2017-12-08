"""
SDK for the Helios Cameras API.

Methods are meant to represent the core functionality in the developer
documentation.  Some may have additional functionality for convenience.

"""
import logging

from dateutil.parser import parse

from heliosSDK.core import SDKCore, ShowMixin, ShowImageMixin, IndexMixin, \
    DownloadImagesMixin, RequestManager


class Cameras(DownloadImagesMixin, ShowImageMixin, ShowMixin, IndexMixin,
              SDKCore):
    CORE_API = 'cameras'
    MAX_THREADS = 32

    def __init__(self):
        self.request_manager = RequestManager(pool_maxsize=self.MAX_THREADS)
        self.logger = logging.getLogger(__name__)

    def index(self, **kwargs):
        return super(Cameras, self).index(**kwargs)

    def show(self, camera_id):
        return super(Cameras, self).show(camera_id)

    def images(self, camera_id, start_time, limit=500):
        # Log entrance
        self.logger.info('Entering images(id=%s, start_time=%s)', camera_id, start_time)

        query_str = '{}/{}/{}/images?time={}&limit={}'.format(self.BASE_API_URL,
                                                              self.CORE_API,
                                                              camera_id,
                                                              start_time,
                                                              limit)

        resp = self.request_manager.get(query_str)
        json_resp = resp.json()

        # log exit
        self.logger.info('Leaving images(N=%s)', json_resp['total'])

        return json_resp

    def images_range(self, camera_id, start_time, end_time, limit=500):
        # Log entrance
        self.logger.info('Entering imagesRange(id=%s, start_time=%s, end_time=%s)',
                         camera_id, start_time, end_time)

        end_time = parse(end_time).utctimetuple()
        output_json = []
        while True:
            data = self.images(camera_id, start_time, limit=limit)

            # Create new name for brevity.
            times = data['times']

            # If not times exist, break and return.
            if data['total'] == 0:
                break

            first = parse(times[0]).utctimetuple()
            last = parse(times[-1]).utctimetuple()

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
                good_times = [x for x in times if parse(x).utctimetuple()
                              < end_time]
                output_json.extend(good_times)
                break

        # Log exit
        self.logger.info('Leaving imagesRange(N=%s)', len(output_json))

        return {'total': len(output_json), 'times': output_json}

    def show_image(self, camera_id, times):
        return super(Cameras, self).show_image(camera_id, times)

    def download_images(self, urls, out_dir=None, return_image_data=False):
        return super(Cameras, self).download_images(urls,
                                                    out_dir=out_dir,
                                                    return_image_data=return_image_data)
