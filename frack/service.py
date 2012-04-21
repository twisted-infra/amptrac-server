# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.
import os, pwd
from twisted.python import usage
from twisted.application.service import Service
from twisted.python.util import sibpath
from frack.db import DBStore, sqlite_connect, postgres_probably_connect
from frack.responder import FrackResponder
from frack.wiring import AMPService, JSONRPCService

class FrackService(Service):

    def __init__(self, dbconnection, ampPort, jsonRPCPort, mediaPath):
        self.store = DBStore(dbconnection)
        self.responder = FrackResponder(self.store)
        self.ampPort = ampPort
        self.jsonRPCPort = jsonRPCPort
        self.mediaPath = mediaPath
        self.amp = None
        self.jsonrpc = None


    def startService(self):
        self.amp = AMPService(self.ampPort, self.responder)
        self.amp.startService()

        self.jsonrpc = JSONRPCService(self.jsonRPCPort, self.responder,
                                      self.mediaPath)
        self.jsonrpc.startService()



class Options(usage.Options):
    synopsis = '[frack options]'

    optParameters = [['postgres_db', None, None,
                      'Name of Postgres database to connect to.'],

                     ['postgres_user', 'u', pwd.getpwuid(os.getuid())[0],
                      'Username for connecting to Postgres.'],

                     ['sqlite_db', None, None,
                      'Path to SQLite database to connect to.'],

                     ['amp', 'a', 'tcp:1352',
                      'Service description for the AMP listener.'],

                     ['jsonrpc', 'j', 'tcp:1353',
                      'Service description for the JSON-RPC listener.'],

                     ['mediapath', 'p', sibpath(__file__, 'media'),
                      'Location of media files for web UI.']]

    longdesc = """Like that other issue tracker, but with different emotions."""



def makeService(config):

    if config['postgres_db'] and config['sqlite_db']:
        raise usage.UsageError("Only one of 'sqlite_db' and 'postgres_db' can be specified.")
    if not config['postgres_db'] and not config['sqlite_db']:
        config['postgres_db'] = 'trac'

    if config['postgres_db']:
        connection = postgres_probably_connect(config['postgres_db'], config['postgres_user'])
    elif config['sqlite_db']:
        connection = sqlite_connect(config['sqlite_db'])

    return FrackService(dbconnection=connection,
                        ampPort=config['amp'],
                        jsonRPCPort=config['jsonrpc'],
                        mediaPath=config['mediapath'])
