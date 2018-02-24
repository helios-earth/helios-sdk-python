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
