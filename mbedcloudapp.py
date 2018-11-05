"""
Author: Geoffrey Van Landeghem (geoffrey.vl@gmail.com)
"""

import requests
import sys
import json
import time

BASEURL='https://api.us-east-1.mbedcloud.com/v2'
APIKEYFILE='mbedapi.key'

class MbedEndpoint:
    def __init__(self, name, type, status):
        self.name=name
        self.type=type
        self.status=status
    def __str__(self):
        return 'name={0}, type={1}, status={2}'.format(self.name, self.type, self.status)

class MbedCloudApiClient:

    def __init__(self):
        self.getHeaders()

    def getHeaders(self):
        fileOnDisk=open(APIKEYFILE,"a+")
        apikey=fileOnDisk.readline().rstrip()
        fileOnDisk.close()
        self.headers = {
            'Content-Type': 'application/json; charset=UTF-8',
            'Accept': 'application/json',
            'Authorization': '{0}'.format(apikey),
            'Connection': 'keep-alive',
        }

    def getNotificationCallback(self):
        url='{0}/notification/callback'.format(BASEURL)
        print('[DEBUG] GET {0}]'.format(url))
        response = requests.get(url, headers=self.headers, timeout=3)
        if response.status_code != 200:
            print('[DEBUG]  => response error [code: {0}, text: {1}]'.format(response.status_code, response.text))
            return ''
        else:
            print('[DEBUG]  => response OK [code: {0}]'.format(response.status_code))
            return response.json()["url"]

    def getAllEndpoints(self):
        eps = []
        url='{0}/endpoints'.format(BASEURL)
        print('[DEBUG] GET {0}]'.format(url))
        response = requests.get(url, headers=self.headers, timeout=3)
        if response.status_code != 200:
            print('[DEBUG]  => response error [code: {0}, text: {1}]'.format(response.status_code, response.text))
        else:
            print('[DEBUG]  => response OK [code: {0}]'.format(response.status_code))
            for ep in response.json():
                eps.append(MbedEndpoint(ep["name"], ep["type"], ep["status"]))
        return eps



if __name__ == '__main__':

    print('[INFO] Start Mbed Cloud Api Client')
    api = MbedCloudApiClient()
    notificationCb = api.getNotificationCallback()
    print('[INFO] Notifications webhook: {0}'.format(notificationCb))
    endpoints = api.getAllEndpoints()
    for ep in endpoints:
        print('[INFO] Endpoint: {0}'.format(ep))