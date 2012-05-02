define(
  ["frack/service", "dojo/_base/query", "dojo/_base/Deferred"],
  function (service, q, Deferred) {
    return {
      displayLoginState: function (targetId, reportError) {
        var d = new Deferred();
        var target = q(targetId);
        function loggedOut() {
          target.innerHTML("<a href='#'>Login / Register</a>");
          var d1 = new Deferred();
          d1.addCallback(gotAssertion);
          d1.addErrback(reportError);
          target.onclick(function(e) {navigator.id.get(d1.callback, {persistent: true}); return false;});
        };
        function gotAssertion(assertion) {
          if (assertion !== null) {
            var r = service.browserIDLogin(assertion);
            r.addCallback(function (response) {
                            if (response.ok) {
                              target.innerHTML("Logged in as " + response.username);
                              localStorage.setItem('trac_key', response.key);
                              localStorage.setItem('trac_username', response.username);
                            } else {
                              loggedOut();
                            }
                            return null;
                          });
            r.addErrback(reportError);
            return r;
          } else {
            loggedOut();
            return null;
          }
        }
        d.addCallback(gotAssertion);
        d.addErrback(reportError);
        var fired = false;
        function foo(v) {
          if (v) {
            if (!fired) {
              d.callback(v);
            }
            fired = true;
          }
        }
        navigator.id.get(foo, {silent: true});
      },
      logout: function () {
        localStorage.removeItem('trac_key');
        localStorage.removeItem('trac_username');
      }
    };
  });