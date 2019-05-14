Using the Core APIs
===================

Creating Core API Instances
---------------------------

Creating an instance of one of the core APIs is done via :meth:`client <helios.client>`.

.. code-block:: python

    import helios

    alerts = helios.client('alerts')
    cameras = helios.client('cameras')
    collections = helios.client('collections')
    observations = helios.client('observations')

Examples
--------

Find alerts
~~~~~~~~~~~

.. code-block:: python

    import helios

    alerts = helios.client('alerts')

    # Retrieve ressults for New York.
    ny_alert_results, failed = alerts.index(state='New York')

    # Gather the camera IDs from the results.
    ny_alert_ids = ny_alert_results.id

    return ny_alert_ids


- ``ny_alert_results`` is an instance of :class:`AlertsFeatureCollection <helios.alerts_api.AlertsFeatureCollection>`.


Find camera times and download images
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import helios
    import numpy as np

    cameras = helios.client('cameras')

    # Find cameras in Maryland.
    md_cam_results, failures = cameras.index(state='Maryland')
    cam_id = md_cam_results.id[0]

    # Find image times for the given camera id.
    image_times = cameras.images(cam_id, '2018-01-01')

    # Download the images.
    show_image_results, failures = cameras.show_image(
        cam_id, image_times, out_dir='/temp/data', return_image_data=True
    )

    return show_image_results, failures

- ``md_cam_results`` is an instance of :class:`CamerasFeatureCollection <helios.cameras_api.CamerasFeatureCollection>`.

  - Access the list of individual features by calling ``md_cam_results.features``.

- ``show_image_results`` is an instance of :class:`ImageCollection <helios.core.structure.ImageCollection>`.

Find observations and work with collections
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import helios
    import requests
    from helios.utilities import parsing_utils

    observations = helios.client('observations')
    collections = helios.collections('collections')

    # Find Observations
    index_results, failures = observations.index(
        state='georgia',
        sensors='sensors[visibility]=0',
        time_min='2018-02-10T18:00Z',
        time_max='2018-02-10T18:15Z'
    )

    # Get id for each observation feature.
    ids = [x.id for x in index_results.features]

    # Convenience properties also exist for combining attributes from all features.
    ids = index_results.id

    # Create new collection.
    new_id = collections.create(
        'Temp Collection', 'example collection', ['test', 'temp']
    )

    # Add Observations to collection.
    payload = [{'observation_id': x} for x in ids]
    add_result, failures = collections.add_image(new_id, payload)

    # Check for http failures.
    if len(add_result.failed) > 0:
        print('Failures occurred!')

    # Simple data analysis - find all unique cameras for the added observation images.
    ims = collections.images(new_id)
    cams = set([parsing_utils.parse_camera(x) for x in ims])


- ``index_results`` is an instance of :class:`ObservationsFeatureCollection <helios.observations_api.ObservationsFeatureCollection>`.

  - Access the list of individual features by calling ``index_results.features``.

Find Observations Based on Sensor Value
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import helios

    obs_inst = helios.client('observations')
    state = 'Maryland'
    bbox = [-169.352,1.137,-1.690,64.008]
    sensors = 'sensors[visibility][min]=0&sensors[visibility][max]=1'
    results, failures = obs.index(state=state, bbox=bbox, sensors=sensors)


Find Observations Transitions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Example for transition from dry/wet to partial/full-snow road conditions:

.. code-block:: python

    import helios
    obs_inst = helios.client('observations')
    # transition from dry/wet to partial/fully-covered snow roads
    sensors = 'sensors[road_weather][data][min]=6&sensors[road_weather][prev][max]=3'
    results, failures = obs.index(sensors=sensors_query)
