# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

from twisted.protocols import amp
from twisted.application.service import Service
from twisted.internet.protocol import ServerFactory
from twisted.internet.endpoints import serverFromString
from twisted.web import static
from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.internet import reactor
from frack.responder import AMPFace, JSONRPCFace

class AMPFactory(ServerFactory):
    def __init__(self, store):
        self.store = store


    def buildProtocol(self, addr):
        face = AMPFace(self.store)
        a = amp.AMP(boxReceiver=face, locator=face)
        a.factory = self
        return a



class AMPService(Service):

    def __init__(self, port, store):
        self.port = port
        self.store = store


    def startService(self):
        self.endpoint = serverFromString(reactor, self.port)
        self.endpoint.listen(AMPFactory(self.store))



class JSONRPCService(Service):
    def __init__(self, port, store, mediaPath):
        self.port = port
        self.store = store
        self.mediaPath = mediaPath


    def startService(self):
        self.endpoint = serverFromString(reactor, self.port)
        self.root = Resource()
        self.root.putChild('amp', JSONRPCFace(self.store))
        self.root.putChild('ui', static.File(self.mediaPath))
        self.site = Site(self.root)
        self.endpoint.listen(self.site)
