import logging

import pytest

import helios

logging.disable(logging.WARNING)


def test_alerts():
    # Create Alerts instance
    alerts = helios.Alerts()

    # Perform index query
    index_results = alerts.index()

    # Extract id from index query
    id_ = index_results[0]['features'][0]['id']

    # Perform show query
    show_results = alerts.show(id_)


if __name__ == '__main__':
    pytest.main([__file__])
