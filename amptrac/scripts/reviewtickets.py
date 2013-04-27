# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

import sys, textwrap, time, datetime
from twisted.internet.endpoints import clientFromString, connectProtocol
from twisted.protocols import amp
from twisted.python import usage
from amptrac.responder import FetchReviewTickets

class Options(usage.Options):
    synopsis = "review-tickets [options]"

    optParameters = [['port', 'p', 'tcp:host=localhost:port=1352',
                      'Service description for the AMP connector.']]



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



def formatTicket(ticket):
    ticket['time'] = convertTime(ticket['time'])
    headline = "* #%(id)s - %(summary)s [%(status)s]\n" % ticket
    subline = ("`-- keywords: %(keywords)s reporter: %(reporter)s "
               "component: %(component)s\n" % ticket)
    sys.__stdout__.write(''.join([headline, subline]))



def formatTickets(response):
    tickets = response['tickets']
    for ticket in tickets:
        formatTicket(ticket)



def main(reactor, *argv):
    config = Options()
    config.parseOptions(argv[1:])
    def fetch(p):
        d = p.callRemote(FetchReviewTickets, asHTML=False)
        d.addCallback(formatTickets)
        return d
    
    d = connectProtocol(clientFromString(reactor, config['port']), amp.AMP())
    d.addCallback(fetch)
    return d
