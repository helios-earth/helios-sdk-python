Using the Core APIs
===================

Creating Instances
------------------

Instances of the core APIs are easy to create.

.. code-block:: python

    import helios
    alerts = helios.Alerts()
    cameras = helios.Cameras()
    observations = helios.Observations()
    collections = helios.Collections()

Each instance will internally initialize a Helios 
:meth:`Session <helios.core.session.Session>` and call 
:meth:`start_session <helios.core.session.Session.start_session>`.


Examples
--------

Find alerts
~~~~~~~~~~~

.. code-block:: python

    import helios
    alerts = helios.Alerts()

    # Retrieve ressults for New York.
    ny_alert_results = alerts.index(state='New York')

    # Gather the camera IDs from the results.
    ny_alert_ids = ny_alert_results.id


- ``ny_alert_results`` is an instance of :class:`AlertsFeatureCollection <helios.alerts_api.AlertsFeatureCollection>`.


Find camera times and download images
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import helios
    import numpy as np

    cameras = helios.Cameras()

    # Find cameras in Maryland.
    md_cam_results = cameras.index(state='Maryland')
    cam_id = md_cam_results.id[0]

    # Find image times for the given camera id.
    image_times = cameras.images(cam_id, '2018-01-01')

    # Download the images.
    show_image_results = cameras.show_image(cam_id,
                                            image_times,
                                            out_dir='/temp/data',
                                            return_image_data=True)

    # Get a list of image data. (return_image_dat was True)
    img_data = show_image_results.image_data


- ``md_cam_results`` is an instance of :class:`CamerasFeatureCollection <helios.cameras_api.CamerasFeatureCollection>`.
- ``show_image_results`` is an instance of :class:`ImageCollection <helios.core.structure.ImageCollection>`.

Find observations and work with collections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import helios
    import requests
    from helios.utilities import parsing_utils

    observations = helios.Observations()
    collections = helios.Collections()

    # Find Observations
    index_results = observations.index(state='georgia',
                                       sensors='sensors[visibility]=0',
                                       time_min='2018-02-10T18:00Z',
                                       time_max='2018-02-10T18:15Z')

    # Get id for each observation feature.
    ids = [x.id for x in index_results.features]

    # Convenience properties also exist for combining attributes from all features.
    ids_1 = index_results.id

    # Create new collection.
    new_id = collections.create('Temp Collection', 'example collection', ['test', 'temp'])

    # Add Observations to collection.
    payload = [{'observation_id': x} for x in ids]
    add_result = collections.add_image(new_id, payload)

    # Check for http failures.
    if len(add_result.failed) > 0:
        print('Failures occurred!')

    # Simple data analysis - find all unique cameras for the added observation images.
    ims = collections.images(new_id)
    cams = set([parsing_utils.parse_camera(x) for x in ims])

- ``index_results`` is an instance of :class:`ObservationsFeatureCollection <helios.observations_api.ObservationsFeatureCollection>`.
- ``add_result`` is an instance of :class:`RecordCollection <helios.core.structure.RecordCollection>`.
