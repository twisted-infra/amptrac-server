from twisted.protocols import amp

class FetchTicket(amp.Command):
    arguments = [('id', amp.Integer())]
    response = [('id', amp.Integer()),
                ('type', amp.Unicode()),
                ('time', amp.Integer()),
                ('component', amp.Unicode()),
                ('priority', amp.Unicode()),
                ('owner', amp.Unicode()),
                ('reporter', amp.Unicode()),
                ('cc', amp.Unicode()),
                ('status', amp.Unicode()),
                ('resolution', amp.Unicode()),
                ('summary', amp.Unicode()),
                ('description', amp.Unicode()),
                ('keywords', amp.Unicode()),
                ('changes', amp.AmpList([('time', amp.Integer()),
                                         ('author', amp.Unicode()),
                                         ('field', amp.Unicode()),
                                         ('oldvalue', amp.Unicode()),
                                         ('newvalue', amp.Unicode())]))]



class FrackResponder(amp.CommandLocator):
    def __init__(self, store):
        self.store = store


    @FetchTicket.responder
    def fetchTicket(self, id):
        d = self.store.fetchTicket(id)
        return d
