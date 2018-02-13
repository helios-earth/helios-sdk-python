.. _session_instances:

Session Instances
=================

A Helios :meth:`Session <helios.core.session.Session>` depends 
on properly established authentication procedures.  See 
:ref:`authentication` for more information.  It also stores your
authentication information and will fetch an API token.  This 
token is required for any API queries.  

Once a session has been created, the token will be written to 
a `.helios_token` file in your home directory.  This token 
will be reused until it becomes invalid.

Creating a Session
------------------

If authentication is stored on your machine starting a session is
simple.  Create a :meth:`Session <helios.core.session.Session>`
instance without any inputs.  The authentication information 
stored on your machine will automatically be applied.

.. code-block:: python

    import helios
    sess = helios.Session()
    
From this point make a call to the 
:meth:`start_session <helios.core.session.Session.start_session>`
method  to fetch the token.

.. code-block:: python

    sess.start_session()
    
If successful, the ``sess`` instance will now have all the
authentication information needed to being using the core APIs.
    
Reusing a Session
-----------------

Creating a :meth:`Session <helios.core.session.Session>` instance allows
you to use a single instance across all Core APIs.  This avoids multiple token
verifications with the initialization of every Core API instance. Refer to
:ref:`helios_session_instances` for more information.

    .. code-block:: python

        import helios
        sess = helios.Session()
        sess.start_session()
        alerts = helios.Alerts(session=sess)
        cameras = helios.Cameras(session=sess)

In the above code ``sess`` is started once and used across
:class:`Alerts <helios.alerts.Alerts>` and
:class:`Cameras <helios.cameras.Cameras>`.

Using a Custom ``env``
----------------------

When creating a :meth:`Session <helios.core.session.Session>` instance
an optional input variable, ``env``, can be used for dynamic 
credential usage.

This optional input must consist of a dictionary containing all 
necessary information for authentication.

.. code-block:: python

   custom_env = {'HELIOS_KEY_ID': 'mykeyid', 'HELIOS_KEY_SECRET': 'mykeysecret'}
   sess = helios.Session(env=custom_env)
   sess.start_session()
