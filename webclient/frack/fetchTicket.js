define(
  ["dojo/rpc/JsonService"],
  function (makeService) {
    var frack = makeService({"serviceUrl": "/amp"});
    return function fetchTicket(id) {
      return frack.callRemote("FetchTicket",
                              {"id": Number(id),
                               "asHTML": true});
    };
  });