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
          target.onclick(function(e) {navigator.id.get(d1.addCallback); return false;});
        };
        function gotAssertion(assertion) {
          if (assertion !== null) {
            var r = service.browserIDLogin(assertion);
            r.addCallback(function (response) {
                            if (response.ok) {
                              target.innerHTML("Logged in as " + response.username);
                            } else {
                              loggedOut();
                            }
                            return null;
                          });
            return r;
          } else {
            loggedOut();
            return null;
          }
        }
        d.addCallback(gotAssertion);
        d.addErrback(reportError);
        function foo(v) {
          console.log("CALLBACK INVOKED");
          console.log(arguments.callee.caller.toString());
          d.callback(v);
        }
        console.log("MODULE LOADED");
        navigator.id.get(foo, {silent: true});
      }
    };
  });