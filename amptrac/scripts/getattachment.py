# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

import sys, textwrap, time, datetime
from twisted.internet.endpoints import clientFromString, connectProtocol
from twisted.protocols import amp
from twisted.python import usage
from amptrac.responder import FetchTicket
import treq

class ListOptions(usage.Options):

    def parseArgs(self, id):
        self['id'] = int(id)

class GetOptions(usage.Options):

    def parseArgs(self, id, filename=None):
        self['id'] = int(id)
        self['filename'] = filename


class Options(usage.Options):
    synopsis = "fetch-tickets [options] <ticket id>"

    optParameters = [['port', 'p', 'tcp:host=localhost:port=1352',
                      'Service description for the AMP connector.']]
    subCommands = [['list', '', ListOptions, 'List attachemts.'],
                   ['get', '', GetOptions, 'Get attachemt.']]
    defaultSubCommand = 'list'

    def postOptions(self):
        self['id'] = self.subOptions['id']


def convertTime(unixtime):
    return datetime.datetime(*time.gmtime(unixtime)[:6])



def wrapParagraphs(content, width, indentLevel):
    indent = " " * indentLevel
    paras = content.split('\r\n\r\n')
    for para in paras:
        yield textwrap.fill(
                    para, width=width - 8,
                    replace_whitespace=False, initial_indent=indent,
                    subsequent_indent=indent) + '\n'



def listAttachments(response):
    response['time'] = convertTime(response['time'])
    headline = "* #%(id)s - %(summary)s [%(status)s]\n" % response
    subline = ("`-- keywords: %(keywords)s reporter: %(reporter)s "
               "component: %(component)s\n" % response)

    attachments = []
    for item in response['attachments']:
        item['time'] = convertTime(item['time'])
        line = ('-- %(filename)s - %(author)s - %(time)s\n' % item)
        if item['description']:
            line += '   %(description)s\n' % item
        attachments.append(line)
    sys.__stdout__.write(''.join([headline, subline] + attachments))


def getAttachment(id, filename):
    url = 'https://twistedmatrix.com/trac/raw-attachment/ticket/%s/%s' % (id, filename)
    d = treq.get(url.encode('utf-8'))
    d.addCallback(treq.content)
    d.addCallback(sys.__stdout__.write)
    return d

def getLastAttachment(response):
    return getAttachment(response['id'], response['attachments'][-1]['filename'])

def connect(config, reactor):
    return connectProtocol(clientFromString(reactor, config['port']), amp.AMP())

def fetchTicket(proto, config):
    return proto.callRemote(FetchTicket, id=config['id'], asHTML=False)


def main(reactor, *argv):
    config = Options()
    config.parseOptions(argv[1:])

    if config.subCommand == 'list':
        return (connect(config)
                .addCallback(fetchTicket, config)
                .addCallback(listAttachments))
    elif config.subCommand == 'get':
        if config.subOptions['filename']:
            return getAttachment(config['id'], config.subOptions['filename'])
        else:
            return (connect(config, reactor)
                    .addCallback(fetchTicket, config)
                    .addCallback(getLastAttachment))
