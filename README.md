# Helios - SDK - Python

[![PyPI](https://img.shields.io/pypi/v/helios-sdk.svg?style=flat-square)](https://pypi.python.org/pypi/helios-sdk)
[![license](https://img.shields.io/github/license/mashape/apistatus.svg?style=flat-square)](https://github.com/harris-helios/helios-sdk-python/blob/master/LICENSE)

Use the Helios APIs in Python.

Helios® weather analytics from Harris Corporation provide fast and accurate local ground weather intelligence to assist organizations with real-time decision making. Helios analyzes content from thousands of existing public and private video cameras, providing immediate confirmation of ground weather condition changes at a detailed local level.

For more information visit [helios.earth](https://helios.earth/).

------------------

## Interacting with the Helios APIs.
This example creates an instance of the Cameras API, queries for New York 
cameras and then parses the camera IDs from the resulting GeoJSON information.

```python
import helios

cameras = helios.Cameras()

# Retrieve GeoJSON Feature Collection for New York state cameras.
ny_cams = cameras.index(state='New York')

# Gather the camera IDs from the results.

# Combines all id attributes from featues in iterable.
ny_cams_ids = ny_cams.id

# Alternatively, you can iterate and extract individual fields.
ny_cams_ids_2 = [x.id for x in ny_cams]

```

------------------

## Installation

To install the Helios SDK use one of the following two methods:

* __Install the Helios SDK from PyPI:__

```sh
pip install helios-sdk
```

* __For the bleeding edge, install from the GitHub source:__

```sh
git clone https://github.com/harris-helios/helios-sdk-python.git
```

Then `cd` to the helios-sdk-python folder and run the install command:

```sh
cd helios-sdk-python
pip install .
```

------------------


## Authentication

All Helios API methods require valid authentication and are protected using the OAuth 2.0 "client credentials" flow.  The general process for authenticating requests involves first requesting an access token using the developer API key pair, and then requesting protected data using the access token.  [Request access](https://www.harris.com/forms/sishelioscontactus) if you would like to obtain an API key.

### Using Environment Variables
1. Add __"helios\_client\_id"__: "your ID key"
2. Add __"helios\_client\_secret"__: "your secret key"
3. Add __"helios\_api\_url"__: "API URL associated with your account credentials"
    * __"helios\_api\_url"__ is optional.

### Using an Authentication File
1. Create a __".helios"__ directory in your home directory.
2. Create a __"credentials.json"__ file in the __".helios"__ directory.
3. Copy and paste the following into the __"credentials.json"__ file and fill in your credentials:
	```json
	{
		"helios_client_id" : "your ID key" ,
		"helios_client_secret" : "your secret key",
		"helios_api_url" : "API URL (optional)"
	}
	```
    * __"helios\_api\_url"__ is optional.  If you do not need a custom API URL,
    then leave this out of your json file.

For more information refer to the authentication [documentation](https://helios.earth/developers/api/authentication/).
