define(
  ["dojo/io-query", "frack/fetchTicket", "frack/ticketPage", "dojo/domReady!"],
  function (ioq, fetchTicket, ticketPage) {
    var queryString = document.location.search.substr(
      document.location.search[0] === "?" ? 1 : 0);
    var urlQueryArgs = ioq.queryToObject(queryString);
    var d = fetchTicket(urlQueryArgs.id);
    d.addCallback(ticketPage.renderTicket);
    d.addErrback(ticketPage.renderError);
  });