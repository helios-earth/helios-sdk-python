.. _session_instances:

HeliosSession
=============

A Helios :class:`HeliosSession <helios.core.session.HeliosSession>` depends
on properly established authentication procedures.  See 
:ref:`authentication` for more information.  It also stores configuration
parameters and your authentication information and will fetch an API token.
This token is required for any API calls.

Once a session has been created, the token will be written to 
a `.helios_token` file in your home directory.  This token 
will be reused until it becomes invalid.

Creating a Session
------------------

If authentication is stored on your machine starting a session is
straightforward using the `with` protocol.  Create a
:class:`HeliosSession <helios.core.session.HeliosSession>`
instance without any inputs.  The authentication information 
stored on your machine will automatically be applied.

.. code-block:: python

    import helios

    with helios.HeliosSession() as sess:
        print(sess)
    
This will automatically make a call to the
:meth:`start_session <helios.core.session.HeliosSession.start_session>`
method to fetch the token.
    
If successful, the ``sess`` instance will now have all the
authentication information needed to being using the core APIs.

Alternatively, you can make a manual call to :meth:`start_session <helios.core.session.HeliosSession.start_session>`.

.. code-block:: python

    import helios

    sess = helios.HeliosSession()
    sess.start_session()
    print(sess)

Token Expiration
~~~~~~~~~~~~~~~~

Restarting Python if your token expires while the SDK is in use is not
necessary.  Make additional :meth:`start_session <helios.core.session.HeliosSession.start_session>`
to perform the token verification process. This will acquire a new token if it
has expired.

HeliosSession Configuration Parameters
--------------------------------------

A :class:`HeliosSession <helios.core.session.HeliosSession>` can be initialized
with various configuration parameters.

E.g. Limit the maximum concurrency:

.. code-block:: python

    import helios

    with helios.HeliosSession(max_concurrency=50) as sess:
        print(sess)

E.g. Override the base directory for storing tokens/credentials.json files:

.. code-block:: python

    import helios

    with helios.HeliosSession(base_dir='/tmp/custom') as sess:
        print(sess)

E.g. Using custom credentials outside of the standard :ref:`authentication`
methods:

.. code-block:: python

   helios_client_id = '*your ID key*',
   helios_client_secret = '*your secret key*',
   helios_api_url = '*optional API URL override*'

   with helios.Session(
       client_id=helios_client_id,
       client_secret=helios_client_secret,
       api_url=helios_api_url
   ) as sess:
       print(sess)
