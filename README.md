# Helios - SDK - Python

Use the Helios APIs in Python.

Helios® weather analytics from Harris Corporation provide fast and accurate local ground weather intelligence to assist organizations with real-time decision making. Helios analyzes content from thousands of existing public and private video cameras, providing immediate confirmation of ground weather condition changes at a detailed local level.

For more information visit [helios.earth](https://helios.earth/).

------------------

## Authentication

All Helios API methods require valid authentication and are protected using the OAuth 2.0 "client credentials" flow.  The general process for authenticating requests involves first requesting an access token using the developer API key pair, and then requesting protected data using the access token.  [Request access](https://www.harris.com/forms/sishelioscontactus) if you would like to obtain an API key.

### Using Environment Variables
1. Add __"HELIOS\_KEY\_ID"__: "your ID key"
2. Add __"HELIOS\_KEY\_SECRET"__: "your secret key"
3. Add __"HELIOS\_API\_URL"__: "API URL associated with your account credentials"
* __"HELIOS\_API\_URL"__ is optional.

### Using an Authentication File
1. Create a ".helios_auth" file in your home directory.
    * *C:\\Users\\[username]\\.helios_auth* on Windows.
2. Copy and paste the following to the ".helios_auth" file and fill in your authentication values:
	```json
	{
		"HELIOS_API_URL" : "API URL", 
		"HELIOS_KEY_ID" : "your ID key" , 
		"HELIOS_KEY_SECRET" : "your secret key"
	}
	```
* __"HELIOS\_API\_URL"__ is optional.

For more information refer to the authentication [documentation](https://helios.earth/developers/api/authentication/).

------------------
  
## Dependencies
* Python 2 or 3
* requests
* pillow
* numpy
* python-dateutil

Installation examples:

`pip install requests pillow numpy python-dateutil`

`conda install requests pillow numpy python-dateutil`

## SDK Documentation
For detailed SDK documentation refer to [DOCUMENTATION.md](https://github.com/harris-helios/helios-sdk-python/blob/master/DOCUMENTATION.md)
