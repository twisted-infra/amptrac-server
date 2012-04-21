# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.
from twisted.protocols import amp
from twisted.application.service import Service
from twisted.internet.protocol import ServerFactory
from twisted.internet.endpoints import serverFromString
from twisted.internet import reactor

class FetchTicket(amp.Command):
    arguments = [('id', amp.Integer())]
    response = [('id', amp.Integer()),
                ('type', amp.Unicode()),
                ('time', amp.Integer()),
                ('component', amp.Unicode()),
                ('priority', amp.Unicode()),
                ('owner', amp.Unicode()),
                ('reporter', amp.Unicode()),
                ('cc', amp.Unicode()),
                ('status', amp.Unicode()),
                ('resolution', amp.Unicode()),
                ('summary', amp.Unicode()),
                ('description', amp.Unicode()),
                ('keywords', amp.Unicode()),
                ('changes', amp.AmpList([('time', amp.Integer()),
                                         ('author', amp.Unicode()),
                                         ('field', amp.Unicode()),
                                         ('oldvalue', amp.Unicode()),
                                         ('newvalue', amp.Unicode())]))]



class FrackResponder(amp.CommandLocator):
    def __init__(self, store):
        self.store = store


    @FetchTicket.responder
    def fetchTicket(self, id):
        d = self.store.fetchTicket(id)
        return d



class AMPFactory(ServerFactory):
    def __init__(self, store):
        self.store = store


    def buildProtocol(self, addr):
        responder = FrackResponder(self.store)
        disp = amp.BoxDispatcher(responder)
        a = amp.AMP(boxReceiver=disp, locator=responder)
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
    pass



class JSONRPCFace(object):
    pass
