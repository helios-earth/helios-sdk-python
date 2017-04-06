'''
Manager for the authorization token required to access the Helios API 

@author: Michael A. Bayer
'''
import json
import os

import requests as r
    
# Fix for Python 2 and 3 compatibility.
try:
    input = raw_input
except NameError:
    pass


class TokenManager(object):
    token_expiration_threshold = 60  # minutes
    token_url = r'https://api.helios.earth/v1/oauth/token'
    
    _token_file = os.path.join(os.path.expanduser('~'), '.helios_token')
    _auth_file = os.path.join(os.path.expanduser('~'), '.helios_auth')
    
    def __init__(self):
        pass
        
    def startSession(self):
        # Check for saved token first. If it doesn't exist then get a token.
        if os.path.exists(self._token_file):
            self.readToken()
            valid_token = self.verifyToken()
            if not valid_token:
                self.getToken()
        else:
            self.getToken()
            
        return self._tokstruct
            
    def getToken(self):        
        self.getAuthCredentials()
        try:    
            data = {'grant_type':'client_credentials'}
            auth = (self._key_id, self._key_secret)
            resp = r.post(self.token_url, data=data, auth=auth, verify=True)
        except:
            token_url_http = 'http' + self.token_url.split('https')[1]
            data = {'grant_type':'client_credentials'}
            auth = (self._key_id, self._key_secret)
            resp = r.post(token_url_http, data=data, auth=auth, verify=True)
            
        token_request = resp.json()
        self._tokstruct = {'name': 'Authorization', 'value': 'Bearer ' + token_request['access_token']}
                
        self.writeToken() 
        
    def readToken(self):
        with open(self._token_file, 'r') as f:
            self._tokstruct = json.load(f)          
            
    def writeToken(self):
        with open(self._token_file, 'w+') as f:
            json.dump(self._tokstruct, f)
                        
    def verifyToken(self):
        resp = r.get(r'https://api.helios.earth/v1/session', headers={self._tokstruct['name']:self._tokstruct['value']}, verify=True)
        json_resp = resp.json()
        
        if json_resp['name'] is None:
            return False
        else:
            expiration_time = json_resp['expires_in'] / 60.0
            if expiration_time < self.token_expiration_threshold:
                self.getToken()
            return True
        
    def getAuthCredentials(self):
        if 'HELIOS_KEY_ID' in os.environ and 'HELIOS_KEY_SECRET' in os.environ:
            self._key_id = os.environ['HELIOS_KEY_ID']
            self._key_secret = os.environ['HELIOS_KEY_SECRET']
        elif os.path.exists(self._auth_file):
            with open(self._auth_file, 'r') as f:
                data = json.load(f)
                self._key_id = data['key_id']
                self._key_secret = data['key_secret']
        else:
            # If all else fail, enter credentials. 
            print('\n\nAuthenticate using your API key pair.')
            self._key_id = input('Enter your id key: ')
            self._key_secret = input('Enter your secret key: ')
            
            with open(self._auth_file, 'w+') as f:
                json.dump({'key_id': self._key_id, 'key_secret' : self._key_secret}, f)
