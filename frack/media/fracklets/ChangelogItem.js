define(["dojo/_base/declare","dijit/_WidgetBase", "dijit/_TemplatedMixin", "dojo/dom-construct", "dojo/query",  "dojo/text!./ChangelogItem.html", "dojo/NodeList-manipulate"],
function(declare, WidgetBase, TemplatedMixin, domC, q, template) {

  return declare([WidgetBase, TemplatedMixin], {
                   templateString: template,
                   baseClass: "printableform",
                   comment: null,
                   buildRendering: function() {
                     var widget = this;
                     widget.inherited(arguments);
                     widget.changes.forEach(
                       function (change) {
                         function insertChangeline(bits) {
                           var line = q(domC.create("li"))
                             .append(q(domC.create("strong", {"class": "column"}))
                                       .text(change.field));
                           bits.forEach(function (b) {line.append(b);});
                           q(widget.changelineList).append(line);
                         }
                         function emstring(str) {
                           return q(domC.create("em")).text(str);
                         }
                         if (change.field == 'description') {
                           insertChangeline([" modified"]);
                         } else if (!change.oldvalue) {
                           insertChangeline(
                             [" set to ",emstring(change.newvalue)]);

                         } else if (!change.newvalue) {
                           insertChangeline([" removed"]);
                         } else {
                           insertChangeline(
                             [" changed from ",
                              emstring(change.oldvalue),
                              " to ",
                              emstring(change.newvalue)]);
                         }
                       });
                   }});
});
