Using the Core APIs
===================

Creating Instances
------------------

All core API instances must be created with a :class:`HeliosSession <helios.core.session.HeliosSession>`.
that contains various configuration parameters.

.. code-block:: python

    import helios

    with helios.HeliosSession() as sess:
        alerts = helios.Alerts(sess)
        cameras = helios.Cameras(sess)
        observations = helios.Observations(sess)
        collections = helios.Collections(sess)

:class:`HeliosSession <helios.core.session.HeliosSession>` supports the context manager protocol.

Upon entering :class:`HeliosSession <helios.core.session.HeliosSession>` a token will try to
be read from file.  If there is no stored token a new token will be requested.

Each API instance will use the same :class:`HeliosSession <helios.core.session.HeliosSession>`
and all configuration parameters associated with that session.

Alternatively, a :class:`HeliosSession <helios.core.session.HeliosSession>` can
be initialized and used outside of `with`, but care must be taken to make
a call to the :meth:`start_session <helios.core.session.HeliosSession.start_session>`
method.

.. code-block:: python

    import helios

    sess = helios.HeliosSession()
    sess.start_session()
    alerts = helios.Alerts(sess)
    cameras = helios.Cameras(sess)
    observations = helios.Observations(sess)
    collections = helios.Collections(sess)

Examples
--------

Find alerts
~~~~~~~~~~~

.. code-block:: python

    import helios

    with helios.HeliosSession() as sess:
        alerts = helios.Alerts(sess)

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

        with helios.HeliosSession() as sess:
            cameras = helios.Cameras(sess)

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

    with helios.HeliosSession() as sess:
        observations = helios.Observations(sess)
        collections = helios.Collections(sess)

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
