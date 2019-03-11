import logging
from datetime import datetime, timedelta

import pytest

import helios

logging.disable(logging.WARNING)


@pytest.fixture
def utc_range():
    f = '%Y-%m-%d'
    end_date = datetime.utcnow().replace(hour=16, minute=0, second=0)
    begin_date = end_date - timedelta(days=2)

    end_date = end_date.strftime(f)
    begin_date = begin_date.strftime(f)

    return begin_date, end_date


def test_cameras(utc_range, helios_session):
    # Create Cameras instance
    cameras = helios.Cameras(helios_session)

    # Perform index query
    index_results = cameras.index(state='new york')

    # Extract id from index query
    id_ = index_results[0].id[0]

    # Perform show query
    show_results = cameras.show(id_)

    # Perform images query
    images_results = cameras.images(id_, utc_range[0], limit=5)
    assert len(images_results) == 5

    # Perform images range query
    images_range_results = cameras.images(id_, utc_range[0], end_time=utc_range[1])

    # Extract a single time
    t = images_results[0]

    # Perform showImage query
    show_image_query = cameras.show_image(id_, t, return_image_data=True)


if __name__ == '__main__':
    pytest.main([__file__])
