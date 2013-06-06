# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.
import os, pwd
from twisted.python import usage
from twisted.application.service import Service
from amptrac.db import DBStore, sqlite_connect, postgres_probably_connect
from amptrac.responder import AmptracResponder
from amptrac.wiring import AMPService

class AmptracService(Service):

    def __init__(self, dbconnection, ampPort):
        self.store = DBStore(dbconnection)
        self.responder = AmptracResponder(self.store)
        self.ampPort = ampPort
        self.amp = AMPService(self.ampPort, self.responder)

    def startService(self):
        self.amp.startService()



class Options(usage.Options):
    synopsis = '[amptrac options]'

    optParameters = [['postgres_db', None, None,
                      'Name of Postgres database to connect to.'],

                     ['postgres_user', 'u', pwd.getpwuid(os.getuid())[0],
                      'Username for connecting to Postgres.'],

                     ['sqlite_db', None, None,
                      'Path to SQLite database to connect to.'],

                     ['amp', 'a', 'tcp:1352',
                      'Service description for the AMP listener.']]

    longdesc = """A postmodern deconstruction of the Python web-based issue tracker."""



def makeService(config):

    if config['postgres_db'] and config['sqlite_db']:
        raise usage.UsageError("Only one of 'sqlite_db' and 'postgres_db' can be specified.")
    if not config['postgres_db'] and not config['sqlite_db']:
        config['postgres_db'] = 'trac'

    if config['postgres_db']:
        connection = postgres_probably_connect(config['postgres_db'], config['postgres_user'])
    elif config['sqlite_db']:
        connection = sqlite_connect(config['sqlite_db'])

    return AmptracService(dbconnection=connection,
                        ampPort=config['amp'])
