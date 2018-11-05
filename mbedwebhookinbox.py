"""
Author: Geoffrey Van Landeghem (geoffrey.vl@gmail.com)
"""

from webhookinbox import BaseWebhookParser, WebhookInbox
import base64
import json

class MbedWebhookParser(BaseWebhookParser):

    def parse(self, method, js=''):
        print('[DEBUG]  mbed: {0} {1}'.format(method, js))
        if js == '':
            return
        jsondata = json.loads(js)
        if jsondata.has_key('async-responses'):
            for asyncresponse in jsondata['async-responses']:
                decoded = base64.b64decode(asyncresponse["payload"])
                print('[INFO] Decoded: {0}'.format(decoded))
        elif jsondata.has_key('registrations'):
            for registration in jsondata['registrations']:
                print('[INFO] Endpoint online: {0} ({1})'.format(registration["ep"], registration["original-ep"]))


if __name__ == '__main__':

    print('[INFO] Get Bin ID')
    inbox = WebhookInbox(MbedWebhookParser())
    inbox.setupBin()
    print('[INFO] Bin {0} Ready!'.format(inbox.binID))
    inbox.getItems()