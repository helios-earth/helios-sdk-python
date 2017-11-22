import heliosSDK
import pytest


def test_observations():
    # Create Observations instance
    observations_instance = heliosSDK.Observations()

    # Perform index query
    index_results = observations_instance.index()

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
