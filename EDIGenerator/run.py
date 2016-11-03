"""
    Azure Functions HTTP Example Code for Python
    
    Created by Anthony Eden
    http://MediaRealm.com.au/
"""

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'lib')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname( __file__ ), '..', 'env/Lib/site-packages')))

import json
from AzureHTTPHelper import HTTPHelper

import base64
import hashlib
import random
import sys
import time

from Crypto.Cipher import AES
from Crypto.Util import number
import hkdf

# This is a little class used to abstract away some basic HTTP functionality
http = HTTPHelper()

ik = http.get["ik"]
scaler = int(http.get["scaler"])
beacon_time_seconds = int(http.get["beacontime"])

"""Return the EID generated by the given parameters."""
tkdata = (
    "\x00" * 11 +
    "\xFF" +
    "\x00" * 2 +
    chr((beacon_time_seconds / (2 ** 24)) % 256) +
    chr((beacon_time_seconds / (2 ** 16)) % 256))

# PrintBinary("Temporary Key data", tkdata)
tk = AES.new(ik, AES.MODE_ECB).encrypt(tkdata)
# PrintBinary("Temporary Key", tk)
beacon_time_seconds = (beacon_time_seconds // 2 ** scaler) * (2 ** scaler)
eiddata = (
    "\x00" * 11 +
    chr(scaler) +
    chr((beacon_time_seconds / (2 ** 24)) % 256) +
    chr((beacon_time_seconds / (2 ** 16)) % 256) +
    chr((beacon_time_seconds / (2 ** 8)) % 256) +
    chr((beacon_time_seconds / (2 ** 0)) % 256))
# PrintBinary("Ephemeral Id data", eiddata)
eid = AES.new(tk, AES.MODE_ECB).encrypt(eiddata)[:8]
# PrintBinary("Ephemeral Id", eid)
eidEncoded = base64.b64encode(eid)

# All data to be returned to the client gets put into this dict
returnData = {
    #HTTP Status Code:
    "status": 200,
    
    #Response Body:
    "body": "{ ""eid"":"+ eidEncoded+" }",
    
    # Send any number of HTTP headers
    "headers": {
        "Content-Type": "application/json"
    }
}

# Output the response to the client
output = open(os.environ['res'], 'w')
output.write(json.dumps(returnData))