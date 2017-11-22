import heliosSDK
import pytest


def test_alerts():
    # Create Alerts instance
    alerts_instance = heliosSDK.Alerts()

    # Perform index query
    index_results = alerts_instance.index()

    # Extract id from index query
    id_ = index_results[0]['features'][0]['id']

    # Perform show query
    show_results = alerts_instance.show(id_)


if __name__ == '__main__':
    pytest.main([__file__])
