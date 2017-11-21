import heliosSDK
import pytest


def test_alerts():
    # Create Alerts instance
    alerts_instance = heliosSDK.Alerts()

    # Perform index query
    index_results = alerts_instance.index()
    assert (all([x is not None for x in index_results]))

    # Extract id from index query
    id_ = index_results[0]['features'][0]['id']
    assert (id_ is not None)

    # Perform show query
    show_results = alerts_instance.show(id_)
    assert (show_results is not None)


if __name__ == '__main__':
    pytest.main([__file__])
