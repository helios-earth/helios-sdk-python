from datetime import datetime, timedelta

import pytest

import helios


@pytest.fixture
def utc_range():
    f = '%Y-%m-%dT%H:%M:%S'
    now = datetime.utcnow()
    yesterday = now - timedelta(days=2)
    begin = yesterday.replace(hour=16, minute=0, second=0)
    end = yesterday.replace(hour=16, minute=30, second=0)

    begin_time = begin.strftime(f)
    end_time = end.strftime(f)

    return begin_time, end_time


def test_observations(utc_range):
    # Create Observations instance
    observations_instance = helios.Observations()

    # Perform index query
    index_results = observations_instance.index(state='new york',
                                                time_min=utc_range[0],
                                                time_max=utc_range[1])

    # Extract id from index query
    for feature in index_results[0]['features']:
        id_ = feature['id']
        try:
            id_.index('error')
        except ValueError:
            break

    # Perform show query
    show_results = observations_instance.show(id_)

    # Perform preview query
    preview_results = observations_instance.preview(id_)

    # Extract URL
    url = preview_results[0]

    # Perform downloadImages query
    download_images_results = observations_instance.download_images(
        url, return_image_data=True)

    # Check download for image data.
    assert (download_images_results[0].size > 0)


if __name__ == '__main__':
    pytest.main([__file__])
