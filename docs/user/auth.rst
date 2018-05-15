.. _authentication:

Authentication
==============

All Helios API methods require valid authentication and are protected using 
the OAuth 2.0 "client credentials" flow.  The general process for 
authenticating requests involves first requesting an access token using the 
developer API key pair, and then requesting protected data using the access 
token.  `Request access <https://www.harris.com/forms/sishelioscontactus>`_
if you would like to obtain an API key.

Using Environment Variables
---------------------------

#. Add **"helios\_client\_id"**: "your ID key"
#. Add **"helios\_client\_secret"**: "your secret key"
#. Add **"helios\_api\_url"**: "API URL associated with your account credentials"

    - **"helios\_api\_url"** is optional.

Using an Authentication File
----------------------------

#. Create a **".helios"** directory in your home directory.
#. Create a **"credentials.json"** file in your **".helios"** directory.
#. Copy and paste the following into the **"credentials.json"** file and fill in
   your authentication values.

    - **"helios\_api\_url"** is optional.  If you do not need a custom API URL
      leave this out of your json file or set to null.

.. code-block:: json

    { 
        "helios_client_id" : "your ID key" ,
        "helios_client_secret" : "your secret key",
        "helios_api_url" : null
    }

For more information refer to the Helios authentication 
`documentation <https://helios.earth/developers/api/authentication/>`_.