from datetime import datetime, timedelta

import pytest

import heliosSDK


@pytest.fixture(scope='module')
def utcRange():
    f = '%Y-%m-%dT%H:%M:%S'
    now = datetime.utcnow()
    yesterday = now - timedelta(days=2)
    begin = yesterday.replace(hour=16, minute=0, second=0)
    end = yesterday.replace(hour=16, minute=30, second=0)

    begin_time = begin.strftime(f)
    end_time = end.strftime(f)

    return begin_time, end_time


def test_observations(utcRange):
    # Create Observations instance
    observations_instance = heliosSDK.Observations()

    # Perform index query
    index_results = observations_instance.index(state='new york',
                                                time_min=utcRange[0],
                                                time_max=utcRange[1])

    # Extract id from index query
    id_ = index_results[0]['features'][0]['id']

    # Perform show query
    show_results = observations_instance.show(id_)

    # Perform preview query
    preview_results = observations_instance.preview(id_)

    # Extract URL
    url = preview_results['url'][0]

    # Perform downloadImages query
    download_images_results = observations_instance.downloadImages(url, return_image_data=True)

    # Check download for image data.
    assert (download_images_results[0].size > 0)


if __name__ == '__main__':
    pytest.main([__file__])
