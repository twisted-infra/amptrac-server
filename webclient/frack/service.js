define(
  ["dojo/rpc/JsonService"],
  /**
   * JSON-RPC request methods.
   */
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
      },

      updateTicket: function (key, ticketid, data) {
        frack.timeout = 3000;
        data.id = ticketid;
        data.key = key;
        return frack.callRemote("UpdateTicket", data);
      }
    };
  });