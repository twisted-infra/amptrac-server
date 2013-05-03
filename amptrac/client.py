# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from twisted.internet.endpoints import (clientFromString, connectProtocol)
from twisted.protocols import amp
from twisted.internet.defer import gatherResults

import treq

from amptrac.responder import FetchTicket, FetchReviewTickets

DEFAULT_AMP_ENDPOINT = 'tcp:port=1352:host=twistedmatrix.com'

def getRawAttachment(id, filename):
    url = 'https://twistedmatrix.com/trac/raw-attachment/ticket/%s/%s' % (id, filename)
    print url
    d = treq.get(url.encode('utf-8'))
    d.addCallback(treq.content)
    return d

class Client(object):
    def __init__(self, proto):
        self._proto = proto

    def fetchTicket(self, id, asHTML=False):
        return self._proto.callRemote(FetchTicket, id=id, asHTML=asHTML)

    def getAttachment(self, id, filename):
        d = gatherResults([self.fetchTicket(id),
                           getRawAttachment(id, filename)], consumeErrors=True)
        def combineResults(r):
            ticket, attachmentBody = r
            for attachment in ticket['attachments']:
                if attachment['filename'] == filename:
                    attachment = attachment.copy()
                    attachment['ticket_id'] = id
                    attachment['body'] = attachmentBody
                    return attachment
            raise Exception
        d.addCallback(combineResults)
        return d

    def reviewTickets(self):
        return (self._proto.callRemote(FetchReviewTickets)
                .addCallback(lambda r: r['tickets']))


def connect(reactor, port='tcp:host=localhost:port=1352'):
    return (connectProtocol(clientFromString(reactor, port), amp.AMP())
            .addCallback(Client))
