define(
  ["dojo/io-query", "frack/service", "frack/browserid",
   "frack/ticketPage", "dojo/domReady!"],
  function (ioq, service, browserid, ticketPage) {
    browserid.displayLoginState("#login-indicator", ticketPage.renderError);
    var queryString = document.location.search.substr(
      document.location.search[0] === "?" ? 1 : 0);
    var urlQueryArgs = ioq.queryToObject(queryString);
    var d = service.fetchTicket(urlQueryArgs.id);
    d.addCallback(ticketPage.renderTicket);
    d.addErrback(ticketPage.renderError);
  });