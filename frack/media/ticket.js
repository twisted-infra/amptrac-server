// Copyright (c) Twisted Matrix Laboratories.
// See LICENSE for details.
require(["dojo/string", "dojo/query", "dojo/rpc/JsonService",
         "dojo/io-query", 'dojo/date/locale',
         "fracklets/TicketBox", "fracklets/ChangelogItem",
         "dojo/NodeList-manipulate", "dojo/domReady!"],
        function(string, q, makeService, ioq, date, TicketBox, ChangelogItem) {

            /** Format a UNIX time as a date. */
            function fromUNIXTime(time) {
                return date.format(new Date(time * 1000));
            }

            /** Group change entries into comment boxes by author and
             * time. */
            function groupComments(changes) {
                var commentnum = 1;
                var commentgroups = [];
                changes.forEach(
                    function (change) {
                        var last = commentgroups[commentgroups.length - 1];
                        if (!last || change.author != last.author
                                  || change.time != last.unixtime) {
                            last = {"commentnum": commentnum,
                                    "time": fromUNIXTime(change['time']),
                                    "unixtime": change['time'],
                                    "author": change['author'],
                                    "changes": []};
                            commentgroups.push(last);
                            commentnum += 1;
                        }
                        if (change.field == 'comment') {
                            last.comment = change.newvalue;
                        } else {
                            last.changes.push(change);
                        }
                    });
                return commentgroups;
            }

            var frack = makeService({"serviceUrl": "/amp"});
            var queryString = document.location.search.substr(
                              document.location.search[0] === "?" ? 1 : 0);
            var urlQueryArgs = ioq.queryToObject(queryString);
            var d = frack.callRemote("FetchTicket", {"id": Number(urlQueryArgs.id),
                                                     "asHTML": true});

            function showIt (response) {
              q("title").text = string.substitute("#${0} (${1}) - Twisted",
                                                  [response.id, response.summary]);
              response["time"] = fromUNIXTime(response["time"]);
              response["changetime"] = fromUNIXTime(response["changetime"]);
              new TicketBox(response).placeAt(q("#ticketbox")[0]);
              groupComments(response.changes).forEach(
                function (commentgroup) {
                  new ChangelogItem(commentgroup).placeAt(q("#changelog")[0]);
                });
            };
            d.addCallback(showIt);

            function displayError(e) {
              var box = q("#errorbox")[0];
              box.textContent = e;
              box.style.display = 'block';

            }
            d.addErrback(displayError);
});