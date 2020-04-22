#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Modified to ignore SSL verification, since I can't currently
# get it to accept proper SSL connections from the Omni CA

import os
import requests
import urllib3

# Silence the SubjectAltNameWarning that our self-signed CA gives
urllib3.disable_warnings(urllib3.exceptions.SubjectAltNameWarning)

__all__ = ['Webhook']


class InvalidPayload(Exception):
    pass


class HTTPError(Exception):
    pass


class Webhook(object):
    """
    Interacts with a Mattermost incoming webhook.
    """

    def __init__(self,
                 url,
                 api_key,
                 channel=None,
                 icon_url=None,
                 username=None):
        self.api_key = api_key
        self.channel = channel
        self.icon_url = icon_url
        self.username = username
        self.url = url
        self.dir = os.path.dirname(__file__)
        # a cert may be needed if you're on a secure office network
        # self.cert_file_path = os.path.join(self.dir, '../certificate_ca.pem')

    def __setitem__(self, channel, payload):
        if isinstance(payload, dict):
            try:
                message = payload.pop('text')
            except KeyError:
                raise InvalidPayload('missing "text" key')
        else:
            message = payload
            payload = {}
        self.send(message, **payload)

    @property
    def incoming_hook_url(self):
        return '{}/hooks/{}'.format(self.url, self.api_key)

    def send(self, message, channel=None, icon_url=None, username=None):
        payload = {'text': message}

        if channel or self.channel:
            payload['channel'] = channel or self.channel
        if icon_url or self.icon_url:
            payload['icon_url'] = icon_url or self.icon_url
        if username or self.username:
            payload['username'] = username or self.username

        r = requests.post(self.incoming_hook_url, json=payload)
        # Or with the cert:
        # r = requests.post(self.incoming_hook_url, json=payload, verify=self.cert_file_path)
        if r.status_code != 200:
            raise HTTPError(r.text)
