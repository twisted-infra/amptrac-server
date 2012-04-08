# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.
import types
import simplejson as json
from twisted.protocols import amp
from twisted.application.service import Service
from twisted.internet.protocol import ServerFactory
from twisted.internet.endpoints import serverFromString
from twisted.web import static
from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET, Site
from twisted.internet.defer import maybeDeferred
from twisted.internet import reactor
from frack.responder import AMPFace

class AMPFactory(ServerFactory):
    def __init__(self, store):
        self.store = store


    def buildProtocol(self, addr):
        face = AMPFace(self.store)
        a = amp.AMP(boxReceiver=face, locator=face)
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
    def __init__(self, port, store, mediaPath):
        self.port = port
        self.store = store
        self.mediaPath = mediaPath


    def startService(self):
        self.endpoint = serverFromString(reactor, self.port)
        self.root = Resource()
        self.root.putChild('amp', JSONRPCFace(self.store))
        self.root.putChild('ui', static.File(self.mediaPath))
        self.site = Site(self.root)
        self.endpoint.listen(self.site)



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
