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
        # Force iterable
        if not isinstance(observation_ids, (list, tuple)):
            observation_ids = [observation_ids]
        n_obs = len(observation_ids)

        # Log entrance
        self.logger.info('Entering preview({} observation_ids)'.format(n_obs))

        # Get number of threads
        num_threads = min(self.MAX_THREADS, n_obs)

        # Process ids.
        if num_threads > 1:
            with ThreadPool(num_threads) as POOL:
                data = POOL.map(self.__previewWorker, observation_ids)
        else:
            data = [self.__previewWorker(observation_ids[0])]

        # Remove errors, if they exist
        data = [x for x in data if x != -1]

        # Check results
        n_data = len(data)
        message = 'Leaving preview({} out of {} successful)'.format(n_data, n_obs)
        if n_data == 0:
            self.logger.error(message)
            return -1
        elif n_data < n_obs:
            self.logger.warning(message)
        else:
            self.logger.info(message)

        return {'url': data}

    def __previewWorker(self, args):
        observation_id = args

        query_str = '{}/{}/{}/preview'.format(self.BASE_API_URL,
                                              self.CORE_API,
                                              observation_id)

        try:
            resp = self.requestManager.get(query_str)
            redirect_url = resp.url[0:resp.url.index('?')]
            # Redirect URLs do not use api credentials
            resp2 = self.requestManager.head(redirect_url, use_api_cred=False)
        except Exception:
            return -1

        # Check header for dud statuses.
        if 'x-amz-meta-helios' in resp2.headers:
            hdrs = json.loads(resp2.headers['x-amz-meta-helios'])

            if hdrs['isOutcast'] or hdrs['isDud'] or hdrs['isFrozen']:
                sys.stderr.write('{} returned a dud image.'.format(redirect_url) + os.linesep)
                sys.stderr.flush()
                return {'url': None}

        return {'url': redirect_url}

    def downloadImages(self, urls, out_dir=None, return_image_data=False):
        return super(Observations, self).downloadImages(urls, out_dir=out_dir, return_image_data=return_image_data)
