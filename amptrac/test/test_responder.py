from twisted.trial import unittest
from twisted.internet.defer import succeed
from twisted.protocols import amp
from amptrac.responder import (
        AmptracResponder, FetchTicket, UpdateTicket, FetchReviewTickets)


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
              'description': "<pre>Let's throw it in the garbage.</pre>",
              'raw_description': "Let's throw it in the garbage.",
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

FAKEREVIEWTICKET = {'id': 1,
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
                   'description': "<pre>Let's throw it in the garbage.</pre>",
                   'raw_description': "Let's throw it in the garbage.",
                   'keywords': 'trac easy',
                   'branch': '',
                   'branch_author': '',
                   'launchpad_bug': '98765'}


class TestCommands(unittest.TestCase):
    """
    Tests for behaviour of Amptrac AMP commands.
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
        resp = AmptracResponder(FakeStore())
        box = FetchTicket.makeArguments({"id": 1, "asHTML": False}, None)
        d = resp.locateResponder("FetchTicket")(box)
        response = amp._stringsToObjects(d.result, FetchTicket.response,
                                         None)
        self.assertEqual(response, FAKETICKET)


    def test_fetchReviewTickets(self):
        """
        The AMP responder for FetchReviewTickets invokes the store's
        `fetchReviewTickets` method and passes the results to the client.
        """
        class FakeStore(object):
            def fetchReviewTickets(f):
                return succeed([FAKEREVIEWTICKET])
        resp = AmptracResponder(FakeStore())
        box = FetchReviewTickets.makeArguments({"asHTML": False}, None)
        d = resp.locateResponder("FetchReviewTickets")(box)
        from twisted.python import log
        d.addErrback(log.err)
        response = amp._stringsToObjects(d.result, FetchReviewTickets.response,
                                         None)
        self.assertEqual(response, {'tickets': [FAKEREVIEWTICKET]})

    def test_updateTicket(self):
        """
        Responder for UpdateTicket sends updates to the store.
        """
        updateData = {
            'type': None,
            'component': None,
            'priority': None,
            'owner': "jethro",
            'reporter': None,
            'cc': None,
            'status': None,
            'resolution': None,
            'summary': "awesome ticket",
            'description': None,
            'keywords': "review",
            'branch': None,
            'branch_author': None,
            'launchpad_bug': None,
            'comment': None
            }
        updates = []
        class FakeStore(object):
            def updateTicket(f, key, ticketid, data):
                self.assertEqual(key, '123abc')
                self.assertEqual(ticketid, 123)
                updates.append(data)

        resp = AmptracResponder(FakeStore())
        box = UpdateTicket.makeArguments(
            {"id": 123, "key": "123abc", "owner": "jethro",
             "summary": "awesome ticket", "keywords": "review"}, None)
        d = resp.locateResponder("UpdateTicket")(box, None)
        amp._stringsToObjects(d.result, UpdateTicket.response,
                                         None)
        self.assertEqual(updates, [updateData])
    test_updateTicket.skip = "This needs authentication, first."
