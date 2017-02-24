#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
import json
import os

from base64 import b64decode
from urllib2 import Request, urlopen, URLError, HTTPError


ENCRYPTED_HOOK_URL = os.environ['kmsEncryptedHookUrl']
SLACK_CHANNEL = os.environ['slackChannel']

HOOK_URL = "https://" + boto3.client('kms').decrypt(CiphertextBlob=b64decode(ENCRYPTED_HOOK_URL))['Plaintext']

def lambda_handler(event, context):
    slack_message = {
        'channel': SLACK_CHANNEL,
        'text': u'%s - %s' % (event['Error'], event['Cause'])
    }

    req = Request(HOOK_URL, json.dumps(slack_message))
    response = urlopen(req)
    response.read()
    return event
