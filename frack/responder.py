# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.
import types
from urllib import quote_plus as qp
try:
    import json
except ImportError:
    import simplejson as json
import cgi
from twisted.protocols import amp
from twisted.web import client
from twisted.web.server import NOT_DONE_YET
from twisted.web.resource import Resource
from twisted.internet.defer import maybeDeferred
from twisted.python import log
try:
    import trac
    from trac.wiki.formatter import format_to_html
    from trac.wiki.parser import WikiParser
    from trac.wiki.api import WikiSystem
    from trac.wiki.interwiki import InterWikiMap
except ImportError:
    trac = None

class FetchTicket(amp.Command):
    arguments = [('id', amp.Integer()),
                 ('asHTML', amp.Boolean())]
    response = [('id', amp.Integer()),
                ('type', amp.Unicode()),
                ('time', amp.Integer()),
                ('changetime', amp.Integer()),
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
                ('branch', amp.Unicode()),
                ('branch_author', amp.Unicode()),
                ('launchpad_bug', amp.Unicode()),
                ('attachments', amp.AmpList(['name', amp.Unicode()])),
                ('changes', amp.AmpList([('time', amp.Integer()),
                                         ('author', amp.Unicode()),
                                         ('field', amp.Unicode()),
                                         ('oldvalue', amp.Unicode()),
                                         ('newvalue', amp.Unicode())]))]


class BrowserIDLogin(amp.Command):
    arguments = [('assertion', amp.Unicode())]
    response = [('email', amp.Unicode()),
                ('username', amp.Unicode()),
                ('key', amp.Unicode())]



class FrackResponder(amp.CommandLocator):
    def __init__(self, store, baseUrl):
        self.store = store
        self.baseUrl = baseUrl


    def _rewriteTicket(self, ticket, transform):
        ticket['description'] = transform(ticket['description'])
        for change in ticket['changes']:
            if change['field'] == 'comment':
                change['newvalue'] = transform(change['newvalue'])


    @FetchTicket.responder
    def fetchTicket(self, id, asHTML):
        d = self.store.fetchTicket(id)
        def _cleanup(ticket):
            if asHTML:
                if trac:
                    self._rewriteTicket(ticket, safeTracWikiFormat)
                else:
                    self._rewriteTicket(ticket, plaintextFormat)
            return ticket
        d.addCallback(_cleanup)

        def _handleErr(e):
            log.err(e)
            return e
        d.addErrback(_handleErr)
        return d


    @BrowserIDLogin.responder
    def browserIDLogin(self, assertion):
        d = client.getPage("https://browserid.org/verify?audience=%s&assertion=%s"
                           % ( self.baseUrl, qp(assertion)), method="POST")
        def _collect(resultData):
            result = json.loads(resultData)
            if result['status'] != 'okay':
                return {'ok': False, 'email': ''}
            return (self.store.lookupByEmail(result['email'])
                    .addCallback(_gotUser, {'ok': True, 'email': result['email']}))
        def _gotUser((key, username), result):
            result['username'] = username
            result['key'] = key
            return result
        return d.addCallback(_collect)



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
