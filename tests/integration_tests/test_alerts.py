import logging

import pytest

import helios

logging.disable(logging.WARNING)


def test_alerts(helios_session):
    # Create Alerts instance
    alerts = helios.Alerts(helios_session)

    # Perform index query
    index_results = alerts.index()

    # Perform show query
    show_results = alerts.show(index_results[0].id[0])


if __name__ == '__main__':
    pytest.main([__file__])
