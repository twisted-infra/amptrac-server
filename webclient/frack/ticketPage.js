define(
  ["dojo/string", "dojo/_base/query", "dojo/date/locale",
   "frack/mustache",  "frack/groupComments",
   "dojo/text!./resources/ticketbox.html",
   "dojo/text!./resources/changelog.html",
   "dojo/NodeList-manipulate"],
  function(string, q, date, Mustache, groupComments, ticketbox, changelog) {
    /** Format a UNIX time as a date. */
    function fromUNIXTime(time) {
      return date.format(new Date(time * 1000));
    }

    /**
     * Find the target DOM node, its corresponding template,
     * and fill the node with the template and data.
     */
    function fill(target, templ, data) {
      var ctempl = Mustache.compile(templ, {"debug": false});
      var rendered = ctempl(data);
      q("#" + target).addContent(rendered);
    }

    return {
      renderTicket: function (response) {
        q("title").append(
          string.substitute("#${0} (${1}) - Twisted",
                            [response.id, response.summary]));
        response["time"] = fromUNIXTime(response["time"]);
        response["changetime"] = fromUNIXTime(response["changetime"]);
        fill("ticketbox", ticketbox, response);
        fill("changelog", changelog, {"changes": groupComments(response.changes)});
      },

      renderError: function displayError(e) {
        var box = q("errorbox");
        box.addClass("system-message");
        box.text(e);
      }
    };
});