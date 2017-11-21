from datetime import datetime, timedelta

import heliosSDK
import pytest


@pytest.fixture(scope='module')
def utcNow():
    f = '%Y-%m-%d'
    end_date = datetime.utcnow()
    begin_date = end_date - timedelta(days=1)

    end_date = end_date.strftime(f)
    begin_date = begin_date.strftime(f)

    return begin_date, end_date


def test_cameras(utcNow):
    # Create Cameras instance
    cameras = heliosSDK.Cameras()

    # Perform index query
    index_results = cameras.index()
    assert (all([x is not None for x in index_results]))

    # Extract id from index query
    id_ = index_results[0]['features'][0]['id']

    # Perform show query
    show_results = cameras.show(id_)
    assert (show_results is not None)

    # Perform images query
    images_results = cameras.images(id_, utcNow[0])
    # TODO: make images return None on error
    assert (images_results is not None)

    # Perform images range query
    images_range_results = cameras.imagesRange(id_, utcNow[0], utcNow[1])
    # TODO: make imagesRange return None on error
    assert (images_range_results is not None)

    # Extract a single time
    t = images_results['times'][0]

    # Perform showImage query
    show_image_query = cameras.showImage(id_, t)
    assert (all([x is not None for x in show_image_query['url']]))

    # Extract URL
    url = show_image_query['url'][0]

    # Perform downloadImages query
    download_images_results = cameras.downloadImages(url, return_image_data=True)
    assert (download_images_results is not None)

    # Check download for image data.
    assert (download_images_results[0].size > 0)


if __name__ == '__main__':
    pytest.main([__file__])
