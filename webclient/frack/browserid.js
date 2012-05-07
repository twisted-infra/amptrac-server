define(
  ["dojo/_base/lang", "dojo/_base/Deferred"],
  function (lang, Deferred) {
    return function (validateAssertion, loginHandler, logoutHandler, reportError) {
      return {
        onLogout: function () {
          var loginTarget = logoutHandler();
          var d1 = new Deferred();
          d1.addCallback(lang.hitch(this, this.onAssertion));
          d1.addErrback(reportError);
          loginTarget.onclick(function(e) {
                                navigator.id.get(lang.hitch(d1, d1.callback),
                                                 {persistent: true});
                                return false;
                              });
        },
        onLogin: function (response) {
          var self = this;
          if (response.ok) {
            var logoutTarget = loginHandler(response);
            logoutTarget.onclick(function (e) {
                                   navigator.id.logout();
                                   self.onLogout();
                                 });
          } else {
            this.onLogout();
          }
        },
        onAssertion: function (assertion) {
          if (assertion !== null) {
            var r = validateAssertion(assertion);
            r.addCallback(lang.hitch(this, this.onLogin));
            r.addErrback(reportError);
            return r;
          } else {
            return null;
          }
        },
        start: function () {
          var self = this;
          var fired = false;
          var d = new Deferred();
          d.addCallback(lang.hitch(this, this.onAssertion));
          d.addErrback(reportError);
          function gotAssertion(assertion) {
            if (assertion) {
              d.callback(assertion);
            } else {
              self.onLogout();
            }
          };
          navigator.id.get(gotAssertion, {silent: true});
        }
      };
    };
  });