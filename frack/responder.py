# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.
import types
try:
    import json
except ImportError:
    import simplejson as json
import cgi
from twisted.protocols import amp
from twisted.web.server import NOT_DONE_YET
from twisted.web.resource import Resource
from twisted.internet.defer import maybeDeferred
from twisted.python import log
try:
    import trac
    from trac.wiki.formatter import format_to_html
    from trac.wiki.parser import WikiParser
    from trac.wiki.api import WikiSystem
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



class AMPFace(amp.BoxDispatcher, amp.CommandLocator):

    def __init__(self, store):
        amp.BoxDispatcher.__init__(self, self)
        self.store = store

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
                    self._rewriteTicket(ticket, trac_wiki_format)
                else:
                    self._rewriteTicket(ticket, plaintext_format)
            return ticket
        return d.addCallback(_cleanup).addErrback(log.err)


def plaintext_format(txt):
    return '<pre style="white-space: pre-line">' + cgi.escape(txt) + '</pre>'


def trac_wiki_format(txt):
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
    return format_to_html(env, Context, txt, False)

UNKNOWN_ERROR, UNHANDLED_ERROR_CODE = (-32603, -32601)

class JSONRPCFace(Resource):

    def __init__(self, store):
        Resource.__init__(self)
        self.ampface = AMPFace(store)


    def _serialize(self, response, request):
        request.write(json.dumps(response))
        request.finish()


    def _err(self, failure, request, qid):
        return self._fail(request, UNKNOWN_ERROR,
                          str(failure.value), qid)


    def _fail(self, request, code, msg, qid):
        self._serialize({"jsonrpc": "2.0",
                         "error":
                             {"code": code,
                              "message": msg},
                         "id": qid},
                        request)


    def _succeed(self, result, request, qid):
        self._serialize({"jsonrpc": "2.0",
                         "result": result,
                         "id": qid},
                        request)


    def _locateResponder(self, name):
        cd = self.ampface._commandDispatch
        if name in cd:
            commandClass, responderFunc = cd[name]
            responderMethod = types.MethodType(
                responderFunc, self.ampface, AMPFace)
            return responderMethod

    def render(self, request):
        q = json.loads(request.content.read())
        qid = q.get('id')
        resp = self._locateResponder(q['method'])
        if resp is None:
            self._fail(request, UNHANDLED_ERROR_CODE,
            "Unhandled Command: %r" % (q['method'],), qid)
        else:
            self._invoke(request, resp, q['params'], qid)
        return NOT_DONE_YET


    def _invoke(self, request, responder, params, qid):
        d = maybeDeferred(responder, **dict([(k.encode('ascii'), v) for (k, v) in params.iteritems()]))
        d.addCallback(self._succeed, request, qid)
        d.addErrback(self._err, request, qid)
        return d


    def getChild(self, path, request):
        if path == '':
            return self
        else:
            return Resource.getChild(self, path, request)
