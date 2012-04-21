# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.
import types
try:
    import json
except ImportError:
    import simplejson as json
from twisted.protocols import amp
from twisted.application.service import Service
from twisted.internet.protocol import ServerFactory
from twisted.internet.endpoints import serverFromString
from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET, Site
from twisted.internet.defer import maybeDeferred
from twisted.internet import reactor
from frack.responder import FrackResponder

class AMPFactory(ServerFactory):
    def __init__(self, store):
        self.store = store


    def buildProtocol(self, addr):
        responder = FrackResponder(self.store)
        disp = amp.BoxDispatcher(responder)
        a = amp.AMP(boxReceiver=disp, locator=responder)
        a.factory = self
        return a



class AMPService(Service):

    def __init__(self, port, store):
        self.port = port
        self.store = store


    def startService(self):
        self.endpoint = serverFromString(reactor, self.port)
        self.endpoint.listen(AMPFactory(self.store))



class JSONRPCService(Service):
    def __init__(self, port, store):
        self.port = port
        self.store = store


    def startService(self):
        self.endpoint = serverFromString(reactor, self.port)
        self.root = JSONRPCFace(self.store)
        self.site = Site(self.root)
        self.endpoint.listen(self.site)



(INVALID_REQUEST, PARSE_ERROR,
 UNKNOWN_ERROR, METHOD_NOT_FOUND
) = (-32600, -32700,
      -32603, -32601)

class JSONRPCFace(Resource):

    def __init__(self, responder):
        Resource.__init__(self)
        self.responder = responder



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
        cd = self.responder._commandDispatch
        if name in cd:
            commandClass, responderFunc = cd[name]
            responderMethod = types.MethodType(
                responderFunc, self.responder, self.responder.__class__)
            return responderMethod


    def render(self, request):
        try:
            q = json.loads(request.content.read())
        except ValueError:
            self._fail(request, PARSE_ERROR,
                      "No JSON object could be decoded", None)
            return NOT_DONE_YET
        qid = q.get('id')
        if 'method' not in q:
            self._fail(request, INVALID_REQUEST, "Not a JSON-RPC request", qid)
            return NOT_DONE_YET
        resp = self._locateResponder(q['method'])
        if resp is None:
            self._fail(request, METHOD_NOT_FOUND,
            "Unhandled Command: %r" % (q['method'].encode('ascii'),), qid)
        else:
            self._invoke(request, resp, q.get('params') or {}, qid)
        return NOT_DONE_YET


    def _invoke(self, request, responder, params, qid):
        d = maybeDeferred(responder,
                          **dict([(k.encode('ascii'), v)
                                  for (k, v) in params.iteritems()]))
        d.addCallback(self._succeed, request, qid)
        d.addErrback(self._err, request, qid)
        return d


    def getChild(self, path, request):
        if path == '':
            return self
        else:
            return Resource.getChild(self, path, request)
