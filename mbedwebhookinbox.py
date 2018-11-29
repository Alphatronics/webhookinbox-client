"""
Author: Geoffrey Van Landeghem (geoffrey.vl@gmail.com)
"""

from webhookinbox import BaseWebhookParser, WebhookInbox
import base64
import json
from dbservice import DbService

DBFILE='requestdb.db'

class MbedWebhookParser(BaseWebhookParser):

    def __init__(self):
        self.db = DbService(DBFILE)
        self.db.connect()

    def parse(self, method, js=''):
        print('[DEBUG]  mbed: {0} {1}'.format(method, js))
        if js == '':
            return
        jsondata = json.loads(js)
        if jsondata.has_key('async-responses'):
            for asyncresponse in jsondata['async-responses']:
                if asyncresponse.has_key('payload'):
                    decoded = base64.b64decode(asyncresponse["payload"])
                    print('[INFO] Decoded: {0}'.format(decoded))
                    self.db.updateNewRequest(asyncresponse["id"], decoded, asyncresponse["status"])
        elif jsondata.has_key('registrations'):
            for registration in jsondata['registrations']:
                print('[INFO] Endpoint online: {0}'.format(registration["ep"]))
        elif jsondata.has_key('notifications'):
            for notification in jsondata['notifications']:
                if notification.has_key('payload'):
                    decoded = base64.b64decode(notification["payload"])
                    print('[INFO] Notification from {0} {1}: {2}'.format(notification["ep"], notification["path"], decoded))


if __name__ == '__main__':

    print('[INFO] Get Bin ID')
    inbox = WebhookInbox(MbedWebhookParser())
    inbox.setupBin()
    print('[INFO] Bin {0} Ready!'.format(inbox.binID))
    inbox.getItems() #loop!