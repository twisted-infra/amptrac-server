// Copyright (c) Twisted Matrix Laboratories.
// See LICENSE for details.
require(["dojo/dom", "dojo/query", "dojo/rpc/JsonService", "dojo/io-query",
         "/ui/mustache.js", "dojo/NodeList-manipulate",  "dojo/domReady!"],
        function(dom, q, makeService, ioq) {

            function fill(target, data) {
                var templ = q("#" + target + "_template")[0].innerHTML;
                var ctempl = Mustache.compile(templ, {"debug": false});
                var rendered = ctempl(data);
                q("#" + target).addContent(rendered);
            }

            var queryObject = ioq.queryToObject(document.location.search.substr(document.location.search[0] === "?" ? 1 : 0));
            var frack = makeService({"serviceUrl": "/amp"});
            var d = frack.callRemote("FetchTicket", {"id": queryObject.id});

            function showIt (response) {

                var commentnum = 1;
                var commentgroups = [];
                var ticketboxData = Object.create(response);

                q("title").append(" #" + response.id + " (" + response.summary + ") - Twisted");

                ticketboxData.description = "<pre>" + response.description + "</pre>";
                ticketboxData.branch = "";
                ticketboxData.branch_author = "";
                ticketboxData.launchpad_bug = "";

                response.changes.forEach(
                    function (change) {
                        var last = commentgroups[commentgroups.length - 1];
                        if (!last || change.author != last.author || change.time != last.time) {
                            last = {"commentnum": commentnum, "time": change['time'], "author": change['author'], "changes": []};
                            commentgroups.push(last);
                            commentnum += 1;
                        }

                        if (change.field == 'comment') {
                            last.comment = '<pre>' +  change['newvalue'] + '</pre>';
                        } else {
                            last.changes.push(change);
                        }
                    });

                fill("ticketbox", ticketboxData);
                fill("changelog", {"changes": commentgroups});
            };
            d.addCallback(showIt);
});