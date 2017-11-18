'''
SDK for the Helios Observations API.  Methods are meant to represent the core
functionality in the developer documentation.  Some may have additional
functionality for convenience.  

@author: mbayer
'''
import json
import logging
import os
import sys
from multiprocessing.dummy import Pool as ThreadPool

from heliosSDK.core import SDKCore, IndexMixin, ShowMixin, DownloadImagesMixin, RequestManager
from heliosSDK.utilities import jsonTools


class Observations(DownloadImagesMixin, ShowMixin, IndexMixin, SDKCore):
    CORE_API = 'observations'
    MAX_THREADS = 32

    def __init__(self):
        self.requestManager = RequestManager(pool_maxsize=self.MAX_THREADS)
        self.logger = logging.getLogger(__name__)

    def index(self, **kwargs):
        return super(Observations, self).index(**kwargs)

    def show(self, observation_id):
        return super(Observations, self).show(observation_id)

    def preview(self, observation_ids):
        if not isinstance(observation_ids, list):
            observation_ids = [observation_ids]

        # Log entrance
        self.logger.info('Entering preview({} observation_ids)'.format(len(observation_ids)))

        # Get number of threads
        num_threads = min(self.MAX_THREADS, len(observation_ids))

        # Process ids.
        if num_threads > 4:
            POOL = ThreadPool(num_threads)
            data = POOL.map(self.__previewWorker, observation_ids)
        else:
            data = map(self.__previewWorker, observation_ids)

        # Remove errors, if they exist
        data = [x for x in data if x is not None]

        # Log success
        self.logger.info('Leaving preview({} out of {} successful)'.format(len(data), len(observation_ids)))

        urls = jsonTools.mergeJson(data, 'url')

        return {'url': urls}

    def __previewWorker(self, args):
        observation_id = args

        query_str = '{}/{}/{}/preview'.format(self.BASE_API_URL,
                                              self.CORE_API,
                                              observation_id)

        # Log query
        self.logger.info('Query began: {}'.format(query_str))

        resp = self.requestManager.get(query_str)

        # Log error and raise exception.
        if not resp.ok:
            self.logger.error('Error {}: {}'.format(resp.status_code, query_str))
            return None

        redirect_url = resp.url[0:resp.url.index('?')]

        # Revert to standard requests package for this.
        resp2 = self.requestManager.head(redirect_url, use_api_cred=False)

        # Log errors
        if not resp2.ok:
            self.logger.error('Error {}: {}'.format(resp2.status_code, redirect_url))
            return None

        # Check header for dud statuses.
        if 'x-amz-meta-helios' in resp2.headers:
            hdrs = json.loads(resp2.headers['x-amz-meta-helios'])

            if hdrs['isOutcast'] or hdrs['isDud'] or hdrs['isFrozen']:
                sys.stderr.write('{} returned a dud image.'.format(redirect_url) + os.linesep)
                sys.stderr.flush()
                return {'url': None}

        # Log success
        self.logger.info('Query complete: {}'.format(query_str))

        return {'url': redirect_url}

    def downloadImages(self, urls, out_dir=None, return_image_data=False):
        return super(Observations, self).downloadImages(urls, out_dir=out_dir, return_image_data=return_image_data)
