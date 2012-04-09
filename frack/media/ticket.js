require(["dojo/dom", "dojo/query", "dojo/rpc/JsonService", "dojo/io-query",
         "dojo/NodeList-manipulate",  "dojo/domReady!"],
        function(dom, q, makeService, ioq) {
            var queryObject = ioq.queryToObject(document.location.search.substr(document.location.search[0] === "?" ? 1 : 0));
            var frack = makeService({"serviceUrl": "/amp"});
            var d = frack.callRemote("FetchTicket", {"id": queryObject.id});
            var showIt = function (response) {
                q("title").append(" #" + response["id"] + " (" + response["summary"] + ") - Twisted");
                q("#ticket-number").text(response["id"]);
                q("h2.summary").text(response["summary"]);
                q(".statuses .type").text(response["type"]);
                q(".statuses .status").text(response["status"]);
                q("#ticket-time").text(response["time"]);
                q("#h_reporter + td").text(response["reporter"]);
                q("#h_owner + td").text(response["owner"]);
                q("#h_priority + td").text(response["priority"]);
                q("#h_component + td").text(response["component"]);
                q("#h_keywords + td").text(response["keywords"]);
                q("#h_cc + td").text(response["cc"]);
                // q("#h_branch + td").text(response["branch"]);
                // q("#h_branch_author + td").text(response["branch_author"]);
                // q("#h_launchpad_bug + td").text(response["launchpad_bug"]);
                q(".description .searchable").append("<pre>" + response["description"] + "</pre>");
                var changelog  = q("#changelog")[0];
                var template = q("form", changelog).orphan();
                var commentnum = 1;
                var commentgroups = [];
                var lastchange = [null, null];
                response["changes"].forEach(
                    function (change) {
                        if (change['author'] != lastchange[0] || change['time'] != lastchange[1]) {
                            commentgroups.push([]);
                            lastchange = [change['author'], change['time']];
                        }
                        commentgroups[commentgroups.length - 1].push(change);
                    });
                commentgroups.forEach(
                    function (group) {
                        var change = template.clone()[0];
                        var linetemplate = q('ul.changes li', change);
                        linetemplate.orphan();
                        var commentid = "#comment:" + commentnum;
                        changelog.appendChild(change);
                        q("a", change).attr('href', commentid);
                        q("h3.change", change).attr("id", commentid);
                        q(".changed-when", change).text(group[0]['time']);
                        q(".changed-by", change).text(group[0]['author']);
                        group.forEach(
                            function (item) {
                                var line = linetemplate.clone()[0];
                                if (item['field'] == 'comment') {
                                    q('.comment', change).addContent("<pre>" + item['newvalue'] + "</pre>");
                                } else {
                                    q('strong.column', line).text(item['field']);
                                    q('.oldvalue', line).text(item['oldvalue']);
                                    q('.newvalue', line).text(item['newvalue']);
                                    q('ul.changes', change).append(line);
                                }
                            });
                    });
            };
            d.addCallback(showIt);
});