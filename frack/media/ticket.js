// Copyright (c) Twisted Matrix Laboratories.
// See LICENSE for details.
require(["dojo/string", "dojo/dom", "dojo/query",
         "dojo/rpc/JsonService", "dojo/io-query",
         "/ui/mustache.js", "dojo/NodeList-manipulate",  "dojo/domReady!"],
        function(string, dom, q, makeService, ioq) {

            /**
              * Find the target DOM node, its corresponding template,
              * and fill the node with the template and data.
             */
            function fill(target, data) {
                var templ = q("#" + target + "_template")[0].innerHTML;
                var ctempl = Mustache.compile(templ, {"debug": false});
                var rendered = ctempl(data);
                q("#" + target).addContent(rendered);
            }

            /** Group change entries into comment boxes by author and
             * time. */
            function groupComments(changes) {
                var commentnum = 1;
                var commentgroups = [];
                var setLineTempl = Mustache.compile(
                    "set to <em>{{newvalue}}</em>");
                var changedLineTempl = Mustache.compile(
                    "changed from <em>{{oldvalue}}</em> to"
                    + " <em>{{newvalue}}</em>");
                changes.forEach(
                    function (change) {
                        var last = commentgroups[commentgroups.length - 1];
                        if (!last || change.author != last.author
                                  || change.time != last.time) {
                            last = {"commentnum": commentnum,
                                    "time": change['time'],
                                    "author": change['author'], "changes": []};
                            commentgroups.push(last);
                            commentnum += 1;
                        }
                        if (change.field == 'comment') {
                            last.comment = change.newvalue;
                        } else {
                            if (change.field == 'description') {
                                change.changeline = "modified";
                            } else if (!change.oldvalue) {
                                change.changeline = setLineTempl(change);
                            } else if (!change.newvalue) {
                                change.changeline = "removed";
                            } else {
                                change.changeline = changedLineTempl(change);
                            }
                            last.changes.push(change);
                        }
                    });
                return commentgroups;
            }

            var frack = makeService({"serviceUrl": "/amp"});
            var queryString = document.location.search.substr(
                              document.location.search[0] === "?" ? 1 : 0);
            var urlQueryArgs = ioq.queryToObject(queryString);
            var d = frack.callRemote("FetchTicket", {"id": Number(urlQueryArgs.id), "asHTML": true});

            function showIt (response) {

                var ticketboxData = Object.create(response);

                q("title").append(string.substitute("#${0} (${1}) - Twisted", [response.id, response.summary]));


                fill("ticketbox", ticketboxData);
                fill("changelog", {"changes": groupComments(response.changes)});
            };
            d.addCallback(showIt);

            function displayError(e) {
                fill("errorbox", {"error": e});
            }
            d.addErrback(displayError);
});