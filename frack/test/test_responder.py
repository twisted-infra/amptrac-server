import json
from twisted.trial import unittest
from twisted.internet.defer import succeed
from twisted.protocols import amp
from twisted.web import client
from frack.responder import FrackResponder, FetchTicket, BrowserIDLogin


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
        resp = FrackResponder(FakeStore(), '')
        box = FetchTicket.makeArguments({"id": 1, "asHTML": False}, None)
        d = resp.locateResponder("FetchTicket")(box)
        response = amp._stringsToObjects(d.result, FetchTicket.response,
                                         None)
        self.assertEqual(response, FAKETICKET)


    def test_browserIDLogin(self):
        """
        Responder for BrowserIDLogin sends a request to the
        browserid.org verification service and then invokes
        `lookupByEmail` on the store.
        """

        def fakeGetPage(url, method):
            self.assertEqual(url, "https://browserid.org/verify"
                             "?audience=https://example.org/&"
                             "assertion=fake-assertion")
            return succeed(json.dumps({'status': 'okay',
                                       'email': 'alice@example.com'}))
        self.patch(client, 'getPage', fakeGetPage)
        class FakeStore(object):
            def lookupByEmail(f, email):
                self.assertEqual(email, 'alice@example.com')
                return succeed(('fake-key', 'alice'))

        resp = FrackResponder(FakeStore(), "https://example.org/")
        box = BrowserIDLogin.makeArguments({'assertion': "fake-assertion"}, None)
        d = resp.locateResponder("BrowserIDLogin")(box)
        response = amp._stringsToObjects(d.result, BrowserIDLogin.response,
                                         None)
        self.assertEqual(response, {'key': 'fake-key', 'email': 'alice@example.com',
                                    'username': 'alice'})