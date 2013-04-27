# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

import sys, textwrap, time, datetime
from twisted.internet.endpoints import clientFromString, connectProtocol
from twisted.protocols import amp
from twisted.python import usage
from amptrac.responder import FetchTicket

class Options(usage.Options):
    synopsis = "fetch-tickets [options] <ticket id>"

    optParameters = [['port', 'p', 'tcp:host=localhost:port=1352',
                      'Service description for the AMP connector.']]

    def parseArgs(self, id):
        self['id'] = int(id)



def termsize():
    import fcntl, termios, struct
    return struct.unpack('hh', fcntl.ioctl(1, termios.TIOCGWINSZ,
                                           '1234'))


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



def format(response):
    height, width = termsize()
    response['time'] = convertTime(response['time'])
    headline = "* #%(id)s - %(owner)s - %(summary)s [%(status)s] - " % response
    subline = ("`-- keywords: %(keywords)s reporter: %(reporter)s "
               "component: %(component)s" % response)
    indent = " " * 4
    body = textwrap.wrap(response['description'], width=width - 8,
                         replace_whitespace=False,
                         initial_indent=indent, subsequent_indent=indent)

    changes = ['\n']
    for item in response['changes']:
        item['time'] = convertTime(item['time'])
        if item['field'] == 'comment':
            changes.append('    ** %(author)s - %(time)s #%(oldvalue)s' % item)
            comment = wrapParagraphs(item['newvalue'], width, 8)
            changes.extend(comment)
            changes.append('\n')
        else:
            changes.append('# %(author)s changed %(field)s: '
                           '%(oldvalue)s -> %(newvalue)s' % item)
    sys.__stdout__.write('\n'.join([headline, subline] + body + changes +
                                   ['\n']))



def main(reactor, *argv):
    config = Options()
    config.parseOptions(argv[1:])
    def fetch(p):
        d = p.callRemote(FetchTicket, id=config['id'], asHTML=False)
        d.addCallback(format)
        return d
    
    d = connectProtocol(clientFromString(reactor, config['port']), amp.AMP())
    d.addCallback(fetch)
    return d
