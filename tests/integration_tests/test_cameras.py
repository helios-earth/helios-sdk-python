from datetime import datetime, timedelta

import pytest

import helios


@pytest.fixture
def utc_now():
    f = '%Y-%m-%d'
    end_date = datetime.utcnow()
    begin_date = end_date - timedelta(days=2)

    end_date = end_date.strftime(f)
    begin_date = begin_date.strftime(f)

    return begin_date, end_date


def test_cameras(utc_now):
    # Create Cameras instance
    cameras = helios.Cameras()

    # Perform index query
    index_results = cameras.index(limit=10, skip=3900)

    # Extract id from index query
    id_ = index_results[0]['features'][0]['id']

    # Perform show query
    show_results = cameras.show(id_)

    # Perform images query
    images_results = cameras.images(id_, utc_now[0])

    # Perform images range query
    images_range_results = cameras.images_range(id_, utc_now[0], utc_now[1])

    # Extract a single time
    t = images_results[0]

    # Perform showImage query
    show_image_query = cameras.show_image(id_, t)

    # Extract URL
    url = show_image_query[0]

    # Perform downloadImages query
    if url is not None:
        download_images_results = cameras.download_images(url,
                                                          return_image_data=True)


if __name__ == '__main__':
    pytest.main([__file__])
