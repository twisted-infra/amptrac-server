define(
  ["dojo/io-query", "dojo/_base/query",
   "frack/service", "frack/browserid",
   "frack/ticketPage", "dojo/domReady!"],
  /**
   * Entry point for ticket page. Hook up BrowserID auth and fetch
   * ticket.
   */
  function (ioq, q, service, browserid, ticketPage) {
    var endLi = q("#metanav .last");
    var target = q("#login-indicator");
    function validate (a) {
      return service.browserIDLogin(a);
    }
    /**
     * Hook up the logout button and store credentials.
     */
    function onLogin(response) {
      var logoutButton = q(document.createElement("li"));
      logoutButton.attr("id", "logout-button");
      logoutButton.innerHTML('<a href="#">Logout</a>');
      target.innerHTML("Logged in as " +
                       response.username + " ");
      logoutButton.insertAfter(target);
      localStorage.setItem('trac_key', response.key);
      localStorage.setItem('trac_username',
                           response.username);
      return logoutButton;

    };
    /**
     * Display login button and scrub credentials.
     */
    function onLogout() {
      q("#logout-button").remove();
      target.innerHTML("<a href='#'>Login / Register</a>");
      localStorage.removeItem('trac_key');
      localStorage.removeItem('trac_username');
      return target;
    }

    var b = browserid(validate, onLogin, onLogout, ticketPage.renderError);
    b.start();
    var queryString = document.location.search.substr(
      document.location.search[0] === "?" ? 1 : 0);
    var urlQueryArgs = ioq.queryToObject(queryString);
    var d = service.fetchTicket(urlQueryArgs.id);
    d.addCallback(ticketPage.renderTicket);
    d.addErrback(ticketPage.renderError);
  });