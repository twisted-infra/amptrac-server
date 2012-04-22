require(
  ["doh/runner", "frack/groupComments"],
  function (doh, groupComments) {
    "use strict";
    doh.register("groupComments",
      [function test_description(self) {
         var change = {"author": "jethro",
                       "field": "description",
                       "newvalue": "description new version etc",
                       "time": 1000000000,
                       "oldvalue": "description old version etc"};
         var fakechanges = [Object.create(change)];
         var newchange = Object.create(change);
         newchange.changeline = "modified";
         var groups = groupComments(fakechanges);
         self.assertEqual(groups, [{"commentnum": 1,
                                    "time": "2001-09-08 20:46",
                                    "unixtime": 1000000000,
                                    "author": "jethro",
                                    "changes": [newchange]}]);

      },
       function test_comment(self) {
         var comment = "super great comment";
         var change = {"author": "jethro",
                       "field": "comment",
                       "newvalue": comment,
                       "time": 1000000000,
                       "oldvalue": "1"};
         var fakechanges = [change];
         var groups = groupComments(fakechanges);
         self.assertEqual(groups, [{"commentnum": 1,
                                               "time": "2001-09-08 20:46",
                                               "unixtime": 1000000000,
                                               "author": "jethro",
                                               "changes": [],
                                               "comment": comment}]);
       },
       function test_propUpdate(self) {
         var oldks = "trac";
         var newks = "trac <easy>";
         var change = {"author": "jethro",
                       "field": "keywords",
                       "oldvalue": oldks,
                       "newvalue": newks,
                       "time": 1000000000};
         var fakechanges = [Object.create(change)];
         var newchange = Object.create(change);
         newchange.changeline = ("changed from <em>trac</em> to "
                                + "<em>trac &lt;easy&gt;</em>");
         var groups = groupComments(fakechanges);
         self.assertEqual(groups, [{"commentnum": 1,
                                               "time": "2001-09-08 20:46",
                                               "unixtime": 1000000000,
                                               "author": "jethro",
                                               "changes": [newchange]}]);
       }
      ]);
  });