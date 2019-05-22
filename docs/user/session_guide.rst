.. _session_instances:

HeliosSession
=============

Manually creating a :class:`HeliosSession <helios.core.session.HeliosSession>`
provides advanced access to a session configuration.

A Helios :class:`HeliosSession <helios.core.session.HeliosSession>` depends
on properly established authentication procedures.  See 
:ref:`authentication` for more information.  It also stores configuration
parameters and your authentication information and will fetch an API token.
This token is required for any API calls.

Creating a Session
------------------

If authentication is stored on your machine starting a session is
straightforward.  Create a :class:`HeliosSession <helios.core.session.HeliosSession>`
instance without any inputs.

.. code-block:: python

    import helios

    sess = helios.HeliosSession()
    
This will automatically fetch a token.
    
If successful, the ``sess`` instance will now have all the
authentication information needed to being using the core APIs.

HeliosSession Configuration Parameters
--------------------------------------

A :class:`HeliosSession <helios.core.session.HeliosSession>` can be initialized
with various configuration parameters.

E.g. Limit the maximum number of threads:

.. code-block:: python

    import helios

    sess = helios.HeliosSession(max_threads=50)

E.g. Override the base directory for storing tokens/credentials.json files:

.. code-block:: python

    import helios

    sess = helios.HeliosSession(base_dir='/tmp/custom')

E.g. Using custom credentials outside of the standard :ref:`authentication`
methods:

.. code-block:: python

   helios_client_id = '*your ID key*',
   helios_client_secret = '*your secret key*',
   helios_api_url = '*optional API URL override*'

   sess = helios.Session(
       client_id=helios_client_id,
       client_secret=helios_client_secret,
       api_url=helios_api_url
   )

Creating Core API Instances
---------------------------

Using a custom :class:`HeliosSession <helios.core.session.HeliosSession>` to
create core API instances is straightforward.

.. code-block:: python

    import helios

    sess = helios.HeliosSession(max_threads=50)
    alerts = sess.client('alerts')
    cameras = sess.client('cameras')
    collections = sess.client('collections')
    observations = sess.client('observations')

Default HeliosSession
---------------------

For most cases the default :class:`HeliosSession <helios.core.session.HeliosSession>`
will suffice.  The default is used when creating instances via the top-level
:meth:`client <helios.client>` call.

E.g.

.. code-block:: python

    import helios

    alerts = helios.client('alerts')
