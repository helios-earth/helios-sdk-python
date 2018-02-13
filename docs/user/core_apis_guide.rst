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
