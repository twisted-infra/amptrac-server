require(
  ["doh/runner", "dojo/_base/kernel", "frack/groupComments"],
  function (doh, dojo, groupComments) {
    "use strict";
    dojo.locale = 'en';
    doh.register("groupComments",
      [function test_description(self) {
         var change = {"author": "jethro",
                       "field": "description",
                       "newvalue": "description new version etc",
                       "time": 1000000000,
                       "oldvalue": "description old version etc"};
         var newchange = {"author": "jethro",
                          "field": "description",
                          "newvalue": "description new version etc",
                          "time": 1000000000,
                          "oldvalue": "description old version etc",
                          "changeline": "modified"};
         var groups = groupComments([change]);
         self.assertEqual(groups, [{"commentnum": 1,
                                    "time": "9/8/01 8:46 PM",
                                    "unixtime": 1000000000,
                                    "author": "jethro",
                                    "changes": [newchange]}],
                         groups.toSource());
      },
       function test_comment(self) {
         var comment = "super great comment";
         var change = {"author": "jethro",
                       "field": "comment",
                       "newvalue": comment,
                       "time": 1000000000,
                       "oldvalue": "1"};
         var groups = groupComments([change]);
         self.assertEqual(groups, [{"commentnum": 1,
                                    "time": "9/8/01 8:46 PM",
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
         var newchange = {"author": "jethro",
                          "field": "keywords",
                          "oldvalue": oldks,
                          "newvalue": newks,
                          "time": 1000000000,
                          changeline: ("changed from <em>trac</em> to "
                                       + "<em>trac &lt;easy&gt;</em>")};
         var groups = groupComments([change]);
         self.assertEqual(groups, [{"commentnum": 1,
                                    "time": "9/8/01 8:46 PM",
                                    "author": "jethro",
                                    "unixtime": 1000000000,
                                    "changes": [newchange]}]);
       }
      ]);
  });
