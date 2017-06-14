'''
Manager for the authorization token required to access the Helios API 

@author: Michael A. Bayer
'''
import json
import os

import requests as r


class TokenManager(object):
    token_expiration_threshold = 60  # minutes
    
    _token_file = os.path.join(os.path.expanduser('~'), '.helios_token')
    _auth_file = os.path.join(os.path.expanduser('~'), '.helios_auth')
    
    __default_api_url = r'https://api.helios.earth/v1/'
    
    def __init__(self):
        self.getAuthCredentials()
        
    def startSession(self):
        # Check for saved token first. If it doesn't exist then get a token.
        if os.path.exists(self._token_file):
            self.readToken()
            try:
                valid_token = self.verifyToken()
                if not valid_token:
                    self.getToken()
            except:
                raise
        else:
            self.getToken()
            
        return self._tokstruct, self.api_url
            
    def getToken(self):        
        try:    
            data = {'grant_type':'client_credentials'}
            auth = (self._key_id, self._key_secret)
            resp = r.post(self.token_url, data=data, auth=auth, verify=True)
        except:
            token_url_http = 'http' + self.token_url.split('https')[1]
            data = {'grant_type':'client_credentials'}
            auth = (self._key_id, self._key_secret)
            resp = r.post(token_url_http, data=data, auth=auth, verify=True)
        
        # If the token cannot be acquired, raise exception.
        resp.raise_for_status()
            
        token_request = resp.json()
        self._tokstruct = {'name': 'Authorization', 'value': 'Bearer ' + token_request['access_token']}
                
        self.writeToken() 
        
    def readToken(self):
        with open(self._token_file, 'r') as f:
            self._tokstruct = json.load(f)          
            
    def writeToken(self):
        with open(self._token_file, 'w+') as f:
            json.dump(self._tokstruct, f)
            
    def deleteToken(self):
        os.remove(self._token_file)
                        
    def verifyToken(self):
        resp = r.get(self.api_url + '/session', headers={self._tokstruct['name']:self._tokstruct['value']}, verify=True)
        resp.raise_for_status()
        
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
            
            # Check for API URL override in environment variables
            if 'HELIOS_API_URL' in os.environ:
                self.api_url = os.environ['HELIOS_API_URL']
                self.token_url = os.environ['HELIOS_API_URL'] + '/oauth/token'
            else:
                self.api_url = self.__default_api_url
                self.token_url = self.__default_api_url + '/oauth/token'
                
        elif os.path.exists(self._auth_file):
            with open(self._auth_file, 'r') as f:
                data = json.load(f)
                self._key_id = data['HELIOS_KEY_ID']
                self._key_secret = data['HELIOS_KEY_SECRET']
                
                # Check for API URL override in .helios_auth file
                if 'HELIOS_API_URL' in data:
                    self.api_url = data['api_url']
                    self.token_url = data['api_url'] + '/oauth/token'
                else:
                    self.api_url = self.__default_api_url
                    self.token_url = self.__default_api_url + '/oauth/token'
        else:
            raise Exception('No credentials could be found. Be sure to set environment variables or .helios_auth file correctly.')