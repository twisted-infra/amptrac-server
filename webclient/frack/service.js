define(
  ["dojo/rpc/JsonService"],
  function (makeService) {
    var frack = makeService({"serviceUrl": "/amp"});
    return {
      fetchTicket: function (id) {
        frack.timeout = 3000;
        return frack.callRemote("FetchTicket",
                                {"id": Number(id),
                                 "asHTML": true});
      },
      browserIDLogin: function (assertion) {
        frack.timeout = 300000;
        return frack.callRemote("BrowserIDLogin",
                                {"assertion": assertion});
      }
    };
  });