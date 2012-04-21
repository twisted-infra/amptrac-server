from twisted.trial import unittest
from twisted.internet.defer import succeed
from twisted.protocols import amp
from frack.responder import FrackResponder, FetchTicket


FAKETICKET = {'id': 1,
              'type': 'enhancement',
              'time': 12345,
              'changetime': 12346,
              'component': 'web',
              'priority': 'high',
              'owner': 'washort',
              'reporter': 'exarkun',
              'cc': '',
              'status': 'open',
              'resolution': '',
              'summary': 'Trac is down',
              'description': "Let's throw it in the garbage.",
              'keywords': 'trac easy',
              'branch': '',
              'branch_author': '',
              'launchpad_bug': '98765',
              'attachments': [],
              'changes': [{'time': 123456,
                           'author': 'washort',
                           'field': 'comment',
                           'oldvalue': '1',
                           'newvalue': 'OK'}]}


class TestCommands(unittest.TestCase):
    """
    Tests for behaviour of Frack AMP commands.
    """

    def test_fetchTicket(self):
        """
        The AMP responder for FetchTicket invokes the store's
        `fetchTicket` method and passes the results to the client.
        """
        ticketid = 1
        class FakeStore(object):
            def fetchTicket(f, id):
                self.assertEqual(id, ticketid)
                return succeed(FAKETICKET)
        resp = FrackResponder(FakeStore())
        box = FetchTicket.makeArguments({"id": 1, "asHTML": False}, None)
        d = resp.locateResponder("FetchTicket")(box)
        response = amp._stringsToObjects(d.result, FetchTicket.response,
                                         None)
        self.assertEqual(response, FAKETICKET)
