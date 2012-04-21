from twisted.trial import unittest
from twisted.protocols import amp
from frack import wiring


class TestCommands(unittest.TestCase):

    def test_fetchTicket(self):
        ticketid = 1
        faketicket = {'id': 1,
                      'type': 'enhancement',
                      'time': 12345,
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
                      'changes': [{'time': 123456,
                                   'author': 'washort',
                                   'field': 'comment',
                                   'oldvalue': '1',
                                   'newvalue': 'OK'}]}

        class FakeStore(object):
            def fetchTicket(f, id):
                self.assertEqual(id, ticketid)
                return faketicket

        face = wiring.AMPFace(FakeStore())
        box = wiring.FetchTicket.makeArguments({"id": 1}, None)
        d = face.locateResponder("FetchTicket")(box)
        response = amp._stringsToObjects(d.result, wiring.FetchTicket.response,
                                         None)
        self.assertEqual(response, faketicket)
