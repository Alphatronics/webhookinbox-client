"""
Author: Geoffrey Van Landeghem (geoffrey.vl@gmail.com)
"""

import requests
import sys
import json
import time

BASEURL='http://api.webhookinbox.com'
BINIDFILE='binid.dat'

class BaseWebhookParser:

    def parse(self, method, js=''):
        print('[DEBUG]  Item: {0} {1}'.format(method, js))

class WebhookInbox:

    def __init__(self, customParser):
        self.binID=''
        self.lastCursor='0'
        self.parser=customParser

    #get a working bin:
    #either continue with a working one or create a new one
    def setupBin(self):
        binIdOK=False
        print('[INFO] looking for postbin id on disk...')
        fileOnDisk=open(BINIDFILE,"a+")
        self.binID=fileOnDisk.readline().rstrip()
        self.lastCursor=fileOnDisk.readline().rstrip()
        fileOnDisk.close()
        if self.binID:
            print('[INFO] found postbin on disk: id={0}, last_cursor={1}, checking state...'.format(self.binID, self.lastCursor))
            url='{0}/i/{1}/refresh/'.format(BASEURL, self.binID)
            print('[DEBUG] POST {0}]'.format(url))
            response = requests.post(url)
            if response.status_code == 200:
                print('[DEBUG]  => response OK [code: {0}]'.format(response.status_code))
                print('[INFO] bin OK! id={0}'.format(self.binID))
                binIdOK=True
            elif response.status_code == 404:
                print('[DEBUG]  => response error [code: {0}] => bin does not exist...'.format(response.status_code))
            else:
                print('[ERROR]  => response error [code: {0}] => exiting...'.format(response.status_code))
                sys.exit()
        else:
            print('[INFO] no postbin found on disk')

        if not binIdOK:
            print('[INFO] requesting new postbin...')
            url='{0}/create/'.format(BASEURL)
            print('[DEBUG] POST {0}'.format(url))
            response = requests.post(url, timeout=3)
            if response.status_code != 200:
                print('[ERROR]  => response error [code: {0}, text:{1}] => exiting...'.format(response.status_code, response.text))
                sys.exit()
            print('[DEBUG]  => response OK [code: {0}]'.format(response.status_code))
            self.binID = response.json()["id"]
            self.lastCursor='0'
            print('[INFO] new bin created! id={0}'.format(self.binID))
            fileOnDisk=open(BINIDFILE,"w")
            fileOnDisk.write(self.binID)
            fileOnDisk.write('\n')
            fileOnDisk.write(self.lastCursor)
            fileOnDisk.close()

    # request bin data
    def getItems(self):
        while True:
            url='{0}/i/{1}/items/?order=created&since=id:{2}'.format(BASEURL, self.binID, self.lastCursor)
            print('[DEBUG] GET {0}]'.format(url))
            response = requests.get(url)
            if response.status_code != 200:
                print('[DEBUG]  => response error [code: {0}, text: {1}]'.format(response.status_code, response.text))
                return
            else:
                print('[DEBUG]  => response OK [code: {0}]'.format(response.status_code))
                js = response.json()
                #iterate over received items
                for item in js['items']:
                    if item["method"]=="PUT":
                        self.parser.parse(item["method"], item["body"])
                    elif item["method"]=="POST":
                        self.parser.parse(item["method"], item["body"])
                    else:
                        self.parser.parse(item["method"])
                    
                #update cursor
                self.updateLastCursor(js["last_cursor"])

    def updateLastCursor(self, last_cursor):
        if self.lastCursor == last_cursor:
            return
        if last_cursor == '':
            last_cursor=0
        print('[DEBUG] updating last_cursor from {0} to {1}'.format(self.lastCursor, last_cursor))
        self.lastCursor = last_cursor
        fileOnDisk=open(BINIDFILE,"w")
        fileOnDisk.write(self.binID)
        fileOnDisk.write('\n')
        fileOnDisk.write(self.lastCursor)
        fileOnDisk.close()



if __name__ == '__main__':

    print('[INFO] Get Bin ID')
    inbox = WebhookInbox(BaseWebhookParser())
    inbox.setupBin()
    print('[INFO] Bin {0} Ready!'.format(inbox.binID))
    inbox.getItems()