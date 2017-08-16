# Helios - SDK - Python

Use the Helios APIs in Python.

------------------

## Authentication

[Documentation](https://helios.earth/developers/api/authentication/)

All Helios API methods require valid authentication and are protected using the OAuth 2.0 "client credentials" flow.  The general process for authenticating requests involves first requesting an access token using the developer API key pair, and then requesting protected data using the access token.  Contact the [Helios Sales Team](mailto:heliossales@harris.com) if you would like to obtain an API key.

Your key pair can be found on the [profile page](https://helios.earth/explore/account).  You can locate this page by clicking the hamburger drop-down menu and selecting your profile.

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

------------------
  
## Dependencies
* Python 2 or 3
* requests
* scipy
* retrying

Installation examples:

`pip install requests retrying scipy`

`conda install requests retrying scipy`

## Documentation
For detailed documentation refer to [DOCUMENTATION.md](https://github.com/harris-helios/helios-sdk-python/blob/master/DOCUMENTATION.md)
