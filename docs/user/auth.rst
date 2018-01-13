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

#. Add **"HELIOS\_KEY\_ID"**: "your ID key"
#. Add **"HELIOS\_KEY\_SECRET"**: "your secret key"
#. Add **"HELIOS\_API\_URL"**: "API URL associated with your account credentials"
  - **"HELIOS\_API\_URL"** is optional.

Using an Authentication File
----------------------------

#. Create a ".helios_auth" file in your home directory.
  - "C:\\Users\\[username]\\.helios_auth" on Windows.
#. Copy and paste the following to the ".helios_auth" file and fill in 
   your authentication values:
  - **"HELIOS\_API\_URL"** is optional.

.. code-block:: json

    { 
        "HELIOS_KEY_ID" : "your ID key" , 
        "HELIOS_KEY_SECRET" : "your secret key",
        "HELIOS_API_URL" : "API URL"
    }

For more information refer to the authentication 
`documentation <https://helios.earth/developers/api/authentication/>`_