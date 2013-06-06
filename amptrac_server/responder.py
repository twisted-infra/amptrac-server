# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.

"""
Definitions of AMP commands for Amptrac and responders for them.
"""

import cgi
from twisted.protocols import amp
from twisted.python import log
try:
    import trac
    from trac.wiki.formatter import format_to_html
    from trac.wiki.parser import WikiParser
    from trac.wiki.api import WikiSystem
    from trac.wiki.interwiki import InterWikiMap
except ImportError:
    trac = None

from amptrac.commands import FetchTicket, FetchReviewTickets


class AmptracResponder(amp.CommandLocator):
    """
    Home to responders for Amptrac's AMP/JSON-RPC commands.

    @param store: A data store object, probably a wrapper for a Trac DB.
    """
    def __init__(self, store):
        self.store = store


    def _rewriteTicket(self, ticket, transform):
        ticket['raw_description'] = ticket['description']
        ticket['description'] = transform(ticket['description'])
        for change in ticket.get('changes', []):
            if change['field'] == 'comment':
                change['newvalue'] = transform(change['newvalue'])


    @FetchTicket.responder
    def fetchTicket(self, id, asHTML):
        """
        @see: L{FetchTicket}
        """
        d = self.store.fetchTicket(id)
        def _cleanup(ticket):
            if asHTML:
                if trac:
                    self._rewriteTicket(ticket, safeTracWikiFormat)
                else:
                    self._rewriteTicket(ticket, plaintextFormat)
            else:
                self._rewriteTicket(ticket, lambda x: x)
            return ticket
        d.addCallback(_cleanup)

        def _handleErr(e):
            log.err(e)
            return e
        d.addErrback(_handleErr)
        return d


    @FetchReviewTickets.responder
    def fetchReviewTickets(self):
        """
        @see: L{FetchReviewTickets}
        """
        d = self.store.fetchReviewTickets()
        def _cleanup(tickets):
            return {'tickets': tickets}
        d.addCallback(_cleanup)

        def _handleErr(e):
            log.err(e)
            return e
        d.addErrback(_handleErr)
        return d


    # @UpdateTicket.responder
    # def updateTicket(self, key, id, **kwargs):
    #    self.store.updateTicket(key, id, kwargs)
    #    return {}


def plaintextFormat(txt):
    return '<pre style="white-space: pre-line">' + cgi.escape(txt) + '</pre>'


def safeTracWikiFormat(txt):
    try:
        return tracWikiFormat(txt)
    except Exception, e:
        log.err(e)
        return plaintextFormat(txt)

def tracWikiFormat(txt):
    WikiSystem.safe_schemes = 'cvs,file,ftp,git,irc,http,https,news,sftp,smb,ssh,svn,svn+ssh'.split(',')
    #WikiSystem.syntax_providers = []
    class Env(object):
        components = {}
        def component_activated(self, _): pass
        def get_db_cnx(self): pass
        def __getitem__(self, key): pass
        project_url = "http://example.com/"
        config = {'intertrac': {}}
    class Context(object):
        def set_hints(self, disable_warnings):
            pass
        resource = None
        req = None
        href = None
        perm = None
        def __call__(self): return self

    env = Env()
    WikiParser.env = env
    InterWikiMap.env = env
    return format_to_html(env, Context, txt, False)
