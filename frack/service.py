# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.
from twisted.python import usage
from twisted.application.service import Service
from frack.db import DBStore
#from frack.inmemory import DBStore
from frack.wiring import AMPService, JSONRPCService

class FrackService(Service):

    def __init__(self, db, ampPort, jsonRPCPort):
        self.dbname = db
        self.ampPort = ampPort
        self.jsonRPCPort = jsonRPCPort
        self.amp = None
        self.jsonrpc = None


    def startService(self):
        self.store = DBStore(self.dbname)
        self.amp = AMPService(self.ampPort, self.store)
        self.amp.startService()
        #self.jsonrpc = JSONRPCService(self.jsonRPCPort, self.store)
        #self.jsonrpc.listen()



class Options(usage.Options):
    synopsis = '[frack options]'

    optParameters = [['db', None, 'trac', 'Name of database to connect to.'],
                     ['amp', 'a', 'tcp:1352', 'Service description for the AMP listener.'],
                     ['jsonrpc', 'j', 'tcp:1353', 'Service description for the JSON-RPC listener.']]

    longdesc = """Like that other issue tracker, but with different emotions."""



def makeService(config):
    return FrackService(db=config['db'], ampPort=config['amp'], jsonRPCPort=config['jsonrpc'])
