# Helios - SDK - Python

Use the Helios APIs in Python.

------------------

## Authentication

[Documentation](https://helios.earth/developers/api/session/)

All Helios API methods require valid authentication and are protected using the OAuth 2.0 "client credentials" flow.  The general process for authenticating requests involves first requesting an access token using the developer API key pair, and then requesting protected data using the access token.  Contact the [Helios Sales Team](mailto:heliossales@harris.com) if you would like to obtain an API key.

Your key pair can be found on the [profile page](https://helios.earth/explore/profile).  You can locate this page by clicking the hamburger drop-down menu and selecting your profile.

### Using Environment Variables
1. Open your account environment variables
2. Add "HELIOS\_KEY\_ID": __"your ID key"__
3. Add "HELIOS\_KEY\_SECRET": __"your secret key"__
4. You may need to log out and log back in for changes to take effect.

### Using an Authentication File
1. Create a ".helios_auth" file in your home directory.
    * *C:\Users\[username]\.helios_auth* on Windows.
2. Copy and paste the following to the ".helios_auth" file and fill in your authentication values:
    * {"key\_id": __"your ID key"__ , "key\_secret": __"your secret key"__}

### Enter Credentials on First Run
1. If you do not use the environment variables or authentication file you will be prompted to enter your ID key and secret Key when you try	to import the heliosSDK.
    * Your credentials will then be written to the .helios_auth file mentioned above.

------------------
  
## Dependencies
* Python 2 or 3
* requests
* scikit-image

Example using Pip:

`pip install requests scikit-image`

## Documentation
For detailed documentation refer to DOCUMENTATION.md.
