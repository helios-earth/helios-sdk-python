from datetime import datetime, timedelta

import pytest

import heliosSDK


@pytest.fixture(scope='module')
def utcNow():
    f = '%Y-%m-%d'
    end_date = datetime.utcnow()
    begin_date = end_date - timedelta(days=2)

    end_date = end_date.strftime(f)
    begin_date = begin_date.strftime(f)

    return begin_date, end_date


def test_cameras(utcNow):
    # Create Cameras instance
    cameras = heliosSDK.Cameras()

    # Perform index query
    index_results = cameras.index(state='new york')

    # Extract id from index query
    id_ = index_results[0]['features'][0]['id']

    # Perform show query
    show_results = cameras.show(id_)

    # Perform images query
    images_results = cameras.images(id_, utcNow[0])

    # Perform images range query
    images_range_results = cameras.imagesRange(id_, utcNow[0], utcNow[1])

    # Extract a single time
    t = images_results['times'][0]

    # Perform showImage query
    show_image_query = cameras.showImage(id_, t)
    assert (show_image_query is not None)

    # Extract URL
    url = show_image_query['url'][0]

    # Perform downloadImages query
    download_images_results = cameras.downloadImages(url,
                                                     return_image_data=True)

    # Check download for image data.
    assert (download_images_results[0].size > 0)


if __name__ == '__main__':
    pytest.main([__file__])
