"""
Author: Geoffrey Van Landeghem (geoffrey.vl@gmail.com)
Python 2
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
        self.buildHeaders()

    def buildHeaders(self):
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
        print('[DEBUG] GET {0}'.format(url))
        response = requests.get(url, headers=self.headers, timeout=3)
        if response.status_code != 200:
            print('[DEBUG]  => response error [code: {0}, text: {1}]'.format(response.status_code, response.text))
            return ''
        else:
            print('[DEBUG]  => response OK [code: {0}]'.format(response.status_code))
            return response.json()["url"]

    def putNotificationCallback(self, callbackUrl):
        url='{0}/notification/callback'.format(BASEURL)
        payload={"url":callbackUrl}
        data = json.dumps(payload)
        print('[DEBUG] PUT {0} {1}'.format(url, data))
        response = requests.put(url, headers=self.headers, timeout=3, data=data)
        if response.status_code != 204:
            print('[DEBUG]  => response error [code: {0}, text: {1}]'.format(response.status_code, response.text))
            return ''
        else:
            print('[DEBUG]  => response OK [code: {0}]'.format(response.status_code))
            return callbackUrl

    def getAllEndpoints(self):
        eps = []
        url='{0}/endpoints'.format(BASEURL)
        print('[DEBUG] GET {0}'.format(url))
        response = requests.get(url, headers=self.headers, timeout=3)
        if response.status_code != 200:
            print('[DEBUG]  => response error [code: {0}, text: {1}]'.format(response.status_code, response.text))
        else:
            print('[DEBUG]  => response OK [code: {0}]'.format(response.status_code))
            for ep in response.json():
                eps.append(MbedEndpoint(ep["name"], ep["type"], ep["status"]))
        return eps

    def postPrintACL(self, deviceId):
        if deviceId == '':
            return
        url='{0}/endpoints/{1}/31006/0/27027'.format(BASEURL, deviceId)
        print('[DEBUG] POST {0}'.format(url))
        response = requests.post(url, headers=self.headers, timeout=3)
        if response.status_code != 202:
            print('[DEBUG]  => response error [code: {0}, text: {1}]'.format(response.status_code, response.text))
        else:
            responseID = response.json()["async-response-id"]
            print('[DEBUG]  => response OK [code: {0}, ID:{1}]'.format(response.status_code, responseID))

    def getSerialNumber(self, deviceId):
        url='{0}/endpoints/{1}/3/0/2'.format(BASEURL, deviceId)
        print('[DEBUG] GET {0}'.format(url))
        response = requests.get(url, headers=self.headers, timeout=3)
        if response.status_code != 202:
            print('[DEBUG]  => response error [code: {0}, text: {1}]'.format(response.status_code, response.text))
            return ''
        else:
            responseID = response.json()["async-response-id"]
            print('[DEBUG]  => response OK [code: {0}, ID:{1}]'.format(response.status_code, responseID))
            return responseID

    def getFirmwareVersion(self, deviceId):
        url='{0}/endpoints/{1}/3/0/3'.format(BASEURL, deviceId)
        print('[DEBUG] GET {0}'.format(url))
        response = requests.get(url, headers=self.headers, timeout=3)
        if response.status_code != 202:
            print('[DEBUG]  => response error [code: {0}, text: {1}]'.format(response.status_code, response.text))
            return ''
        else:
            responseID = response.json()["async-response-id"]
            print('[DEBUG]  => response OK [code: {0}, ID:{1}]'.format(response.status_code, responseID))
            return responseID

class MbedCloudApiClientApp:

    def __init__(self):
        self.client = MbedCloudApiClient()
        self.endpoints = []
        self.selectedDeviceId=''

    def setup(self):
        notificationCb = self.client.getNotificationCallback()
        if notificationCb == '':
            print('[INFO] No notifications webhook configured')
            userInput = raw_input('# Do you want to configure one? (Y/n): ')
            if userInput=='n' or userInput=='N':
                return
            userInput = raw_input('# Enter webhook url: ')
            notificationCb = self.client.putNotificationCallback(userInput)
            if notificationCb == '':
                print('[ERROR] Notifications webhook not configured')
                return
        print('[INFO] Notifications webhook: {0}'.format(notificationCb))

    def selectDevice(self):
        if self.selectedDeviceId != '':
            userInput = raw_input('# continue using current device? (Y/n): ')  # Python 2
            if userInput!='n' and userInput!='N':
                return
        self.endpoints = self.client.getAllEndpoints()
        ctr=1
        for ep in self.endpoints:
            print('[INFO] Endpoint {0}: {1}'.format(ctr, ep))
            ctr = ctr+1

        if ctr == 1:
            print('[INFO] No devices found...')
            return
        userInput = raw_input('# Select device (1 ... {0}): '.format(ctr-1))  # Python 2
        try: 
            selectedDevice = int(userInput)
        except ValueError:
            selectedDevice = 0
        if selectedDevice > 0 and selectedDevice < (ctr):
            self.selectedDeviceId = self.endpoints[selectedDevice-1].name
            print('[INFO] Selected device {0}: {1}'.format(selectedDevice, self.selectedDeviceId))
        else:
            print('[ERROR] No device selected...')

    def runDevice_Menu(self):
        print('[INFO] 1. get Serial number')
        print('[INFO] 1. get Firmware version')
        userInput = raw_input('# Select command (1 ... 2): ')
        try: 
            selectedCmd = int(userInput)
        except ValueError:
            selectedCmd = 0
        if selectedCmd == 0:
            print('[ERROR] Illegal choice')
            return
        if selectedCmd == 1:
            print('[INFO] Getting Serial Number ...')
            self.client.getSerialNumber(self.selectedDeviceId)
        elif selectedCmd == 2:
            print('[INFO] Getting Firmware Version ...')
            self.client.getFirmwareVersion(self.selectedDeviceId)

    def runACL_Menu(self):
        print('[INFO] 1. Print ACL')
        userInput = raw_input('# Select command (1 ... 1): ')
        try: 
            selectedCmd = int(userInput)
        except ValueError:
            selectedCmd = 0
        if selectedCmd == 0:
            print('[ERROR] Illegal choice')
            return
        print('[INFO] Print ACL ...')
        self.client.postPrintACL(self.selectedDeviceId)

    def run(self):
        if self.selectedDeviceId == '':
            return
        print('[INFO] 1. Device Info')
        print('[INFO] 2. ACL')
        userInput = raw_input('# Select command (1 ... 2): ')
        try: 
            selectedCmd = int(userInput)
        except ValueError:
            selectedCmd = 0
        if selectedCmd == 0:
            print('[ERROR] Illegal choice')
            return
        if selectedCmd == 1:
            self.runDevice_Menu()
        elif selectedCmd == 2:
            self.runACL_Menu()
        
if __name__ == '__main__':

    print('[INFO] Start Mbed Cloud Api Client App')
    apiclient = MbedCloudApiClientApp()
    apiclient.setup()
    while True: 
        apiclient.selectDevice()
        apiclient.run()
        userInput = raw_input('# Quit application? (y/N): ')
        if userInput=='y' or userInput=='Y':
            break