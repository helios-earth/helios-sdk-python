import logging

import pytest

import helios

logging.disable(logging.WARNING)


def test_alerts():
    # Create Alerts instance
    alerts = helios.Alerts()

    # Perform index query
    index_results = alerts.index()

    # Perform show query
    show_results = alerts.show(index_results.id[0])


if __name__ == '__main__':
    pytest.main([__file__])
