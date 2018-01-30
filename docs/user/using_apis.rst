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
:meth:`~helios.core.session.Session` and call 
:meth:`~helios.core.session.Session.start_session`.  This is
not efficient, but does work.  

Instead you should create a session, start it, and then use this 
for the duration of your work.
    
    
Reusing a Session
-----------------

Creating a session instance allows you to use a single instance 
across all Core APIs.

    .. code-block:: python

        import helios
        sess = helios.Session()
        sess.start_session()
        alerts = helios.Alerts(session=sess)
        cameras = helios.Cameras(session=sess)
        
In the above code `sess` is started once and used across the 
Alerts and Cameras.