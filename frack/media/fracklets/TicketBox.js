define(["dojo/_base/declare","dijit/_WidgetBase", "dijit/_TemplatedMixin", "dojo/text!./TicketBox.html"],
    function(declare, WidgetBase, TemplatedMixin, template) {
        return declare([WidgetBase, TemplatedMixin], {
                           templateString: template,
                           baseClass: "ticketbox-yay"
                       });
    });
