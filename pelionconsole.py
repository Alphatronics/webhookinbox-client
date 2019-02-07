"""
Author: Geoffrey Van Landeghem (geoffrey.vl@gmail.com)
Python 2
"""

import requests
import sys
import json
import time
import os
from dbservice import DbService

BASEURL='https://api.us-east-1.mbedcloud.com/v2'
APIKEYFILE='mbedapi.key'
DEFAULTTIMEOUT=120

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
        print('[DEBUG] Request : GET {0}'.format(url))
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
        print('[DEBUG] Request : PUT {0} {1}'.format(url, data))
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
        print('[DEBUG] Request : GET {0}'.format(url))
        response = requests.get(url, headers=self.headers, timeout=3)
        if response.status_code != 200:
            print('[DEBUG]  => response error [code: {0}, text: {1}]'.format(response.status_code, response.text))
        else:
            print('[DEBUG]  => response OK [code: {0}]'.format(response.status_code))
            for ep in response.json():
                eps.append(MbedEndpoint(ep["name"], ep["type"], ep["status"]))
        return eps

    def __getEndpointData(self, deviceId, uri):
        if deviceId == '':
            return ''
        url='{0}/endpoints/{1}{2}'.format(BASEURL, deviceId, uri)
        print('[DEBUG] Request : GET {0}'.format(url))
        response = requests.get(url, headers=self.headers, timeout=3)
        if response.status_code != 202:
            print('[DEBUG]  => response error [code: {0}, text: {1}]'.format(response.status_code, response.text))
            return ''
        else:
            responseID = response.json()["async-response-id"]
            print('[DEBUG]  => response OK [code: {0}, ID:{1}]'.format(response.status_code, responseID))
            return responseID

    def __postEndpointCommand(self, deviceId, uri):
        if deviceId == '':
            return
        url='{0}/endpoints/{1}{2}'.format(BASEURL, deviceId, uri)
        print('[DEBUG] Request : POST {0}'.format(url))
        response = requests.post(url, headers=self.headers, timeout=3)
        if response.status_code != 202:
            print('[DEBUG]  => response error [code: {0}, text: {1}]'.format(response.status_code, response.text))
            return ''
        else:
            responseID = response.json()["async-response-id"]
            print('[DEBUG]  => response OK [code: {0}, ID:{1}]'.format(response.status_code, responseID))
            return responseID

    def __postEndpointData(self, deviceId, uri, data):
        if deviceId == '':
            return ''
        url='{0}/endpoints/{1}{2}'.format(BASEURL, deviceId, uri)
        print('[DEBUG] Request : POST {0}'.format(url))
        response = requests.post(url, headers=self.headers, timeout=3, data=data)
        if response.status_code != 202:
            print('[DEBUG]  => response error [code: {0}, text: {1}]'.format(response.status_code, response.text))
            return ''
        else:
            responseID = response.json()["async-response-id"]
            print('[DEBUG]  => response OK [code: {0}, ID:{1}]'.format(response.status_code, responseID))
            return responseID

    def getSerialNumber(self, deviceId):
        return self.__getEndpointData(deviceId, '/3/0/2')

    def getModelNumber(self, deviceId):
        return self.__getEndpointData(deviceId, '/3/0/1')

    def getFirmwareVersion(self, deviceId):
        return self.__getEndpointData(deviceId, '/3/0/3')

    def getTime(self, deviceId):
        return self.__getEndpointData(deviceId, '/3/0/13')

    def getDeviceType(self, deviceId):
        return self.__getEndpointData(deviceId, '/3/0/17')

    def getHardwareVersion(self, deviceId):
        return self.__getEndpointData(deviceId, '/3/0/18')

    def postReboot(self, deviceId):
        return self.__postEndpointCommand(deviceId, '/3/0/4')

    def postStandbyCommand(self, deviceId):
        return self.__postEndpointCommand(deviceId, '/31000/0/27010')

    def postFactoryResetCommand(self, deviceId):
        return self.__postEndpointCommand(deviceId, '/3/0/5')

    def postLoadACL(self, deviceId, data):
        return self.__postEndpointData(deviceId, '/31006/0/27025', data)

    def postSyncACL(self, deviceId, data):
        return self.__postEndpointData(deviceId, '/31006/0/27020', data)

    def postPrintACL(self, deviceId):
        return self.__postEndpointCommand(deviceId, '/31006/0/27027')

    def getUploadRecordsData(self, deviceId):
        return self.__getEndpointData(deviceId, '/31007/0/27022')

    def postRequestUploadRecords(self, deviceId, timestamp):
        return self.__postEndpointData(deviceId, '/31007/0/27023', timestamp)

    def postPrintRecordsFilenames(self, deviceId):
        return self.__postEndpointCommand(deviceId, '/31007/0/27028')

    def postScreen(self, deviceId, screenid, data):
        return self.__postEndpointData(deviceId, '/31008/{0}/27000'.format(screenid), data)

    def postIcon(self, deviceId, iconid, data):
        return self.__postEndpointData(deviceId, '/31008/{0}/27001'.format(iconid), data)






DBFILE='requestdb.db'
BINIDFILE='binid.dat'
WEBHOOKURL='http://api.webhookinbox.com'

class PelionConsole:

    def __init__(self):
        self.client = MbedCloudApiClient()
        self.endpoints = []
        self.selectedDeviceId=''
        self.db = DbService(DBFILE)

    def setup(self):
        self.db.connect()

        #look for callback url on disk
        notificationCb = ''
        fileOnDisk=open(BINIDFILE,"a+")
        binID=fileOnDisk.readline().rstrip()
        fileOnDisk.close()
        if binID:
            print('[INFO] found webhook on disk: id={0}, checking state...'.format(binID))
            notificationCb = self.client.getNotificationCallback()
            url='{0}/i/{1}/in/'.format(WEBHOOKURL, binID)
            if binID not in notificationCb:
                print('[INFO] webhook mismatch detected, setting new: {0} (old: {1})'.format(url, notificationCb))
                notificationCb = self.client.putNotificationCallback(url)
        if notificationCb == '':
            print('[ERROR] Notifications webhook not configured')
        else:
            print('[INFO] Notifications webhook: {0}'.format(notificationCb))

    def selectDevice(self):
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

    def waitForResponse(self, responseId):
        print('[DEBUG] waiting for async response...')  
        ctr=0
        while True:
            resp = self.db.getRequest(responseId)
            if resp != None and resp[3] != None:
                print('[INFO] {0}: {1} [STATUS={2}]'.format(resp[1], resp[2], resp[3]))
                return resp[2]
            if ctr >= DEFAULTTIMEOUT:
                print('[ERROR] {0}: TIMEOUT!'.format(resp[1]))
                return None
            time.sleep(1)
            ctr=ctr+1

    def getSerialNumber(self):
        cmd="GET Serial Number"
        print('[INFO] {0} ...'.format(cmd))
        responseId = self.client.getSerialNumber(self.selectedDeviceId)
        if responseId == '':
            return
        ret = self.db.insertNewRequest(responseId, cmd)
        if ret < 1:
            return
        self.waitForResponse(responseId)

    def getModelNumber(self):
        cmd="GET Model Number"
        print('[INFO] {0} ...'.format(cmd))
        responseId = self.client.getModelNumber(self.selectedDeviceId)
        if responseId == '':
            return
        ret = self.db.insertNewRequest(responseId, cmd)
        if ret < 1:
            return
        self.waitForResponse(responseId)
        
    def getFirmwareVersion(self):
        cmd="GET Firmware Version"
        print('[INFO] {0} ...'.format(cmd))
        responseId = self.client.getFirmwareVersion(self.selectedDeviceId)
        if responseId == '':
            return
        ret = self.db.insertNewRequest(responseId, cmd)
        if ret < 1:
            return
        self.waitForResponse(responseId)

    def getTime(self):
        cmd="GET Time"
        print('[INFO] {0} ...'.format(cmd))
        responseId = self.client.getTime(self.selectedDeviceId)
        if responseId == '':
            return
        ret = self.db.insertNewRequest(responseId, cmd)
        if ret < 1:
            return
        self.waitForResponse(responseId)

    def getDeviceType(self):
        cmd="GET Device type"
        print('[INFO] {0} ...'.format(cmd))
        responseId = self.client.getDeviceType(self.selectedDeviceId)
        if responseId == '':
            return
        ret = self.db.insertNewRequest(responseId, cmd)
        if ret < 1:
            return
        self.waitForResponse(responseId)

    def getHardwareVersion(self):
        cmd="GET Hardware version"
        print('[INFO] {0} ...'.format(cmd))
        responseId = self.client.getHardwareVersion(self.selectedDeviceId)
        if responseId == '':
            return
        ret = self.db.insertNewRequest(responseId, cmd)
        if ret < 1:
            return
        self.waitForResponse(responseId)

    def uploadRecords(self):
        self.__eraseDirectory('./Records')

        print('[INFO] Upload records ...')

        # we start with requesting epoch 0 (1/1/1970 0h00m00s)
        timestamp = '0000'
        
        while True:
            epoch = timestamp[:-3]
            datetimeStr = time.strftime("%Y-%m-%d", time.gmtime(long(epoch)))
            print('[INFO] Request upload records from ts {0}, date={1}'.format(timestamp, datetimeStr))
            cmd="POST Requerst Upload Records ts={0}".format(timestamp)
            print('[INFO] {0} ...'.format(cmd))
            responseId = self.client.postRequestUploadRecords(self.selectedDeviceId, timestamp)
            if responseId == '':
                return
            dbRet = self.db.insertNewRequest(responseId, cmd)
            if dbRet < 1:
                return
            ret = self.waitForResponse(responseId)
            if ret == None or ret != 'OK':
                print('[ERROR] Request Upload Records fault detected, sequence stopped')
                return

            # get record data
            cmd="GET record data".format()
            print('[INFO] {0} ...'.format(cmd))
            responseId = self.client.getUploadRecordsData(self.selectedDeviceId)
            if responseId == '':
                return
            dbRet = self.db.insertNewRequest(responseId, cmd)
            if dbRet < 1:
                return
            ret = self.waitForResponse(responseId)
            if ret == None or ret == '' or len(ret)<2:
                print('[ERROR] Get Record Data fault detected, sequence stopped')
                return

            if len(ret)>=15:
                print('[INFO] received records from ts {0}, date={1}'.format(epoch, datetimeStr)) 

                # save to disk using timestamp as filename
                filename='./Records/RECORD_'+epoch+'.db'
                print('[DEBUG] storing records in file {0}'.format(filename))
                try:
                    fileOnDisk=open(filename,"a")
                    fileOnDisk.write(ret[2:])
                    fileOnDisk.close()
                    print('[DEBUG] record data stored')  
                except Exception:
                    print('[ERROR] writing record data to file {0}...'.format(filename))
                    return

            # check if we need request more records
            isLastPacket = bool(ord(ret[1]))
            if isLastPacket == True:
                break

            print('[DEBUG] Scanning next timestamp...')  
            # scan records and look for last timestamp
            nextTs=''
            offsetFromEndOfFile=100
            while True:
                offs=len(ret) - offsetFromEndOfFile
                if offs < 2: # make sure we don't rewind past start-of-data
                    offs=2
                    offsetFromEndOfFile = offsetFromEndOfFile - (len(ret) - offsetFromEndOfFile - 2)
                end = offs + 13
                if end >= len(ret): # reached end of data
                    break
                if end-offs != 13: # did my calculus fail somehow?
                    break

                nextTs = ret[offs:end]
                if ';' not in nextTs: # no ; => we found a 13char timestamp? let's try to parse it...
                    try:
                        long(nextTs)
                        timestamp = nextTs
                    except Exception:
                        pass  # Pretend nothing happened.
                offsetFromEndOfFile = offsetFromEndOfFile-1

            if timestamp == None or timestamp == '':
                print('[ERROR] Could not find last record in record data...') 
                return
            
            print('[INFO] Found timestamp {0}, requesting next record data...'.format(timestamp))  

        print('[INFO] Upload records completed!') 


    def __eraseDirectory(self, dir):
        print('[INFO] erasing directory: {0}'.format(dir))
        filenames=os.listdir(dir)
        for filename in filenames:
            userInput = raw_input('# Remove {0} ? (y/N):'.format(filename))
            if userInput=='y' or userInput=='Y':
                os.remove(dir + '/' + filename)
        
    def loadAcl(self):
        print('[INFO] Load ACL ...')
        print('[DEBUG] reading ACL directory...')
        filenames=os.listdir("./ACL")
        
        ctr=1
        for filename in filenames:
            filename='./ACL/'+filename
            data=''
            try:
                fileOnDisk=open(filename,"rb")
                data=fileOnDisk.read()
                fileOnDisk.close()
            except Exception:
                print('[ERROR] loading ACL from file {0}...'.format(filename))
                return

            print('[INFO] ACL packet {0}/{1}, bytes: {2}, filename: {3}'.format(ctr, len(filenames), len(data), filename))
            cmd="POST Load ACL {0}/{1}".format(ctr, len(filenames))
            print('[INFO] {0} ...'.format(cmd))
            responseId = self.client.postLoadACL(self.selectedDeviceId, data)
            if responseId == '':
                return
            dbRet = self.db.insertNewRequest(responseId, cmd)
            if dbRet < 1:
                return
            ret = self.waitForResponse(responseId)
            if ret == None or ret != '1':
                print('[ERROR] Load ACL fault detected, sequence stopped')
                return
            ctr=ctr+1
        print('[INFO] Load ACL completed!')    

    def syncAcl(self):
        print('[INFO] Sync ACL ...')
        print('[DEBUG] reading ACL directory...')
        filenames=os.listdir("./ACL")
        
        ctr=1
        for filename in filenames:
            filename='./ACL/'+filename
            data=''
            try:
                fileOnDisk=open(filename,"rb")
                data=fileOnDisk.read()
                fileOnDisk.close()
            except Exception:
                print('[ERROR] loading ACL from file {0}...'.format(filename))
                return

            print('[INFO] ACL packet {0}/{1}, bytes: {2}, filename: {3}'.format(ctr, len(filenames), len(data), filename))
            cmd="POST Sync ACL {0}/{1}".format(ctr, len(filenames))
            print('[INFO] {0} ...'.format(cmd))
            responseId = self.client.postSyncACL(self.selectedDeviceId, data)
            if responseId == '':
                return
            dbRet = self.db.insertNewRequest(responseId, cmd)
            if dbRet < 1:
                return
            ret = self.waitForResponse(responseId)
            if ret == None or ret != '1':
                print('[ERROR] Sync ACL fault detected, sequence stopped')
                return
            ctr=ctr+1
        print('[INFO] Sync ACL completed!')  

    def updateScreens(self):
        print('[INFO] updating Screens ...')
        print('[DEBUG] reading Screens directory...')
        filenames=os.listdir("./Screens")
        
        ctr=1
        for filename in filenames:
            filenameRelative='./Screens/'+filename
            data=''
            try:
                fileOnDisk=open(filenameRelative,"rb")
                data=fileOnDisk.read()
                fileOnDisk.close()
            except Exception:
                print('[ERROR] loading Screen from file {0}...'.format(filenameRelative))
                return

            bitmapfIDStr = filename.split('.')[0]
            bitmapID = int(bitmapfIDStr)

            print('[INFO] Screen {0} (nr {1} of total {2}), bytes: {3}, filename: {4}'.format(bitmapID, ctr, len(filenames), len(data), filenameRelative))
            cmd="POST Update Screen {0}/{1}".format(ctr, len(filenames))
            print('[INFO] {0} ...'.format(cmd))
            responseId = self.client.postScreen(self.selectedDeviceId, bitmapID, data)
            if responseId == '':
                return
            dbRet = self.db.insertNewRequest(responseId, cmd)
            if dbRet < 1:
                return
            ret = self.waitForResponse(responseId)
            if ret == None or ret != '1':
                print('[ERROR] Update screen detected, sequence stopped')
                return
            ctr=ctr+1
        print('[INFO] Update screens completed!')  

    def updateIcons(self):
        print('[INFO] updating Icons ...')
        print('[DEBUG] reading Icons directory...')
        filenames=os.listdir("./Icons")
        
        ctr=1
        for filename in filenames:
            filenameRelative='./Icons/'+filename
            data=''
            try:
                fileOnDisk=open(filenameRelative,"rb")
                data=fileOnDisk.read()
                fileOnDisk.close()
            except Exception:
                print('[ERROR] loading Icon from file {0}...'.format(filenameRelative))
                return

            bitmapfIDStr = filename.split('.')[0]
            bitmapID = int(bitmapfIDStr)

            print('[INFO] Icon {0} (nr {1} of total {2}), bytes: {3}, filename: {4}'.format(bitmapID, ctr, len(filenames), len(data), filenameRelative))
            cmd="POST Update Icon {0}/{1}".format(ctr, len(filenames))
            print('[INFO] {0} ...'.format(cmd))
            responseId = self.client.postIcon(self.selectedDeviceId, bitmapID, data)
            if responseId == '':
                return
            dbRet = self.db.insertNewRequest(responseId, cmd)
            if dbRet < 1:
                return
            ret = self.waitForResponse(responseId)
            if ret == None or ret != '1':
                print('[ERROR] Update Icon detected, sequence stopped')
                return
            ctr=ctr+1
        print('[INFO] Update Icons completed!')   




############################ MENUS ############################
    def showDeviceMenu(self):
        print('[SELECT] 1. get Serial number')
        print('[SELECT] 2. get Model number')
        print('[SELECT] 3. get Firmware version')
        print('[SELECT] 4. post Reboot')
        print('[SELECT] 5. post Standby')
        print('[SELECT] 6. post Factory reset')
        print('[SELECT] 7. get time')
        print('[SELECT] 8. get device type')
        print('[SELECT] 9. get hardware version')
        userInput = raw_input('# Select command (1 ... 9): ')
        try: 
            selectedCmd = int(userInput)
        except ValueError:
            selectedCmd = 0
        if selectedCmd < 1 or selectedCmd > 9:
            print('[ERROR] Illegal choice')
        elif selectedCmd == 1:
            self.getSerialNumber()
        elif selectedCmd == 2:
            self.getModelNumber()
        elif selectedCmd == 3:
            self.getFirmwareVersion()
        elif selectedCmd == 4:
            print('[INFO] Reboot device ...')
            self.client.postReboot(self.selectedDeviceId)
        elif selectedCmd == 5:
            print('[INFO] Standby device ...')
            self.client.postStandbyCommand(self.selectedDeviceId)
        elif selectedCmd == 6:
            print('[INFO] Factory reset ...')
            self.client.postFactoryResetCommand(self.selectedDeviceId) 
        elif selectedCmd == 7:
            self.getTime()
        elif selectedCmd == 8:
            self.getDeviceType()
        elif selectedCmd == 9:
            self.getHardwareVersion()

    def showAclMenu(self):
        print('[SELECT] 1. Print ACL')
        print('[SELECT] 2. Load ACL')
        print('[SELECT] 3. Sync ACL')
        userInput = raw_input('# Select command (1 ... 3): ')
        try: 
            selectedCmd = int(userInput)
        except ValueError:
            selectedCmd = 0
        if selectedCmd < 1 or selectedCmd > 3:
            print('[ERROR] Illegal choice')
        elif selectedCmd == 1:
            print('[INFO] Print ACL ...')
            self.client.postPrintACL(self.selectedDeviceId)
        elif selectedCmd == 2:
            self.loadAcl()
        elif selectedCmd == 3:
            self.syncAcl()


    def showRecordsMenu(self):
        print('[SELECT] 1. Upload records')
        print('[SELECT] 2. Print records filenames')
        userInput = raw_input('# Select command (1 ... 2): ')
        try: 
            selectedCmd = int(userInput)
        except ValueError:
            selectedCmd = 0
        if selectedCmd < 1 or selectedCmd > 2:
            print('[ERROR] Illegal choice')
        elif selectedCmd == 1:
            self.uploadRecords()
        elif selectedCmd == 2:
            self.client.postPrintRecordsFilenames(self.selectedDeviceId)

    def showScreensMenu(self):
        print('[SELECT] 1. Update screens')
        print('[SELECT] 2. Update icons')
        userInput = raw_input('# Select command (1 ... 2): ')
        try: 
            selectedCmd = int(userInput)
        except ValueError:
            selectedCmd = 0
        if selectedCmd < 1 or selectedCmd > 2:
            print('[ERROR] Illegal choice')
        elif selectedCmd == 1:
            self.updateScreens()
        elif selectedCmd == 2:
            self.updateIcons()


    def showDeviceManagementMenu(self):
        self.selectDevice()
        if self.selectedDeviceId == '':
            return
        while True:
            print('[SELECT] 1. Device Info')
            print('[SELECT] 2. ACL')
            print('[SELECT] 3. Records')
            print('[SELECT] 4. Screens')
            userInput = raw_input('# Select command (1 ... 4): ')
            try: 
                selectedCmd = int(userInput)
            except ValueError:
                selectedCmd = 0
            if selectedCmd < 1 or selectedCmd > 3:
                print('[ERROR] Illegal choice')
            elif selectedCmd == 1:
                self.showDeviceMenu()
            elif selectedCmd == 2:
                self.showAclMenu()
            elif selectedCmd == 3:
                self.showRecordsMenu()
            elif selectedCmd == 4:
                self.showScreensMenu()

            userInput = raw_input('# continue using current device? (Y/n): ')  # Python 2
            if userInput!='n' and userInput!='N':
                continue
            break

    def showMainMenu(self):
        print('[SELECT] 1. Device Management')
        print('[SELECT] 2. Update firmware campaign')
        userInput = raw_input('# Select command (1 ... 2): ')
        try: 
            selectedCmd = int(userInput)
        except ValueError:
            selectedCmd = 0
        if selectedCmd < 1 or selectedCmd > 2:
            print('[ERROR] Illegal choice')
        elif selectedCmd == 1:
            self.showDeviceManagementMenu()
        elif selectedCmd == 2:
            print('[ERROR] not yet supported')

############################ MAIN ############################
        
if __name__ == '__main__':

    print('[INFO] Start Mbed Cloud Api Client Console')
    apiclient = PelionConsole()
    apiclient.setup()
    while True: 
        apiclient.showMainMenu()
        userInput = raw_input('# Quit application? (y/N): ')
        if userInput=='y' or userInput=='Y':
            break