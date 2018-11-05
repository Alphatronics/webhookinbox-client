"""
Author: Geoffrey Van Landeghem (geoffrey.vl@gmail.com)
"""

from webhookinbox import BaseWebhookParser, WebhookInbox

class MbedWebhookParser(BaseWebhookParser):

    def parse(self, method, js=''):
        print('[DEBUG]  mbed: {0} {1}'.format(method, js))


if __name__ == '__main__':

    print('[INFO] Get Bin ID')
    inbox = WebhookInbox(MbedWebhookParser())
    inbox.setupBin()
    print('[INFO] Bin {0} Ready!'.format(inbox.binID))
    inbox.getItems()