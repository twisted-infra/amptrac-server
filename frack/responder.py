# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.
import types
try:
    import json
except ImportError:
    import simplejson as json
from twisted.protocols import amp
from twisted.web.server import NOT_DONE_YET
from twisted.web.resource import Resource
from twisted.internet.defer import maybeDeferred
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


    @FetchTicket.responder
    def fetchTicket(self, id):
        d = self.store.fetchTicket(id)
        return d


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
