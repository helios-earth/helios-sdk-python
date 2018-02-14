import logging
from datetime import datetime, timedelta

import pytest

import helios

logging.disable(logging.WARNING)


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
    observations = helios.Observations()

    # Perform index query
    index_results = observations.index(state='new york',
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
    show_results = observations.show(id_)

    # Perform preview query
    preview_results = observations.preview(id_, return_image_data=True)[0]

    # Check image data.
    assert (preview_results.data.size > 0)


if __name__ == '__main__':
    pytest.main([__file__])
