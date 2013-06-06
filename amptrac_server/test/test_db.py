import sqlite3
from twisted.trial.unittest import TestCase
from twisted.python.util import sibpath
from amptrac.db import DBStore, UnauthorizedError



class DBTests(TestCase):
    """
    Tests for storage/retrieval.
    """

    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.executescript(open(sibpath(__file__, "trac_test.sql")).read())

    def test_fetchTicket(self):
        """
        `fetchTicket` collects data about a single ticket, including
        comments/changes, attachments, and custom fields.
        """

        store = DBStore((sqlite3, self.db))
        d = store.fetchTicket(4712)
        def _check(result):
            self.assertEqual(set(result.keys()),
                             {"type", "status", "summary", "time", "reporter",
                              "owner", "priority",  "resolution", "component",
                              "keywords", "cc", "branch", "branch_author",
                              "launchpad_bug", "description", "changes",
                              "attachments", "id", "changetime"})

            self.assertEqual(len(result['changes']), 45)
            self.assertEqual(set(result['changes'][0].keys()),
                             {"newvalue", "author", "oldvalue", "time", "field"})
            
            self.assertEqual(len(result['attachments']), 0)

        return d.addCallback(_check)


    def test_fetchTicket_attachments(self):
        """
        `fetchTicket` collects data about a single ticket, including
        comments/changes, attachments, and custom fields.
        """

        store = DBStore((sqlite3, self.db))
        d = store.fetchTicket(5517)
        def _check(result):
            self.assertEqual(set(result.keys()),
                             {"type", "status", "summary", "time", "reporter",
                              "owner", "priority",  "resolution", "component",
                              "keywords", "cc", "branch", "branch_author",
                              "launchpad_bug", "description", "changes",
                              "attachments", "id", "changetime"})

            self.assertEqual(len(result['changes']), 17)
            self.assertEqual(set(result['changes'][0].keys()),
                             {"newvalue", "author", "oldvalue", "time", "field"})
            
            self.assertEqual(len(result['attachments']), 1)
            self.assertEqual(set(result['attachments'][0].keys()),
                             {"id", "filename", "size", "time", "description", "author"})

        return d.addCallback(_check)



    def test_fetchReviewTickets(self):
        """
        `fetchReviewTicket` returns all tickets currently in review.
        """
        store = DBStore((sqlite3, self.db))
        d = store.fetchReviewTickets()
        def _check(results):
            for result in results:
                self.assertEqual(set(result.keys()),
                                 {"type", "status", "summary", "time", "reporter",
                                  "owner", "priority",  "resolution", "component",
                                  "keywords", "cc", "branch", "branch_author",
                                  "launchpad_bug", "id", "changetime"})
            self.assertEqual(set([row['id'] for row in results]),
                    set([5622]))

        return d.addCallback(_check)



    def test_unauthorizedUpdate(self):
        """
        `updateTicket` raises an exception if the key given is
        unacceptable.
        """
        store = DBStore((sqlite3, self.db))
        d = store.updateTicket('not-a-key', 123, {})
        return self.assertFailure(d, UnauthorizedError)


    def test_updateTicket(self):
        """
        `updateTicket` updates the db entry for the given ticket.
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
            #branch is the same as its current value so no change should be recorded
            'branch': "branches/provide-statinfo-accessors-4712",
            'branch_author': "bob",
            'launchpad_bug': None,
            'comment': None
            }
        c = self.db.cursor()
        store = DBStore((sqlite3, self.db))
        c.execute(
            "SELECT summary, owner, keywords from ticket where id = 4712")
        oldSummary, oldOwner, oldKeywords = c.fetchall()[0]
        c.execute("""SELECT value from ticket_custom
                         where ticket = 4712 and name = 'branch_author'""")
        oldBranchAuthor = c.fetchall()[0][0]
        c.execute("select count(*) from ticket_change where ticket = 4712")
        numComments = c.fetchone()[0]
        d = store.updateTicket('a331422278bd676f3809e7a9d8600647', 4712,
                               updateData)
        def _checkDB(_):
            c.execute(
                "SELECT summary, owner, keywords from ticket where id = 4712")
            self.assertEqual(c.fetchall(),
                             [('awesome ticket', 'jethro', 'review')])
            c.execute("""SELECT time
                               from ticket_change where ticket = 4712
                               order by time desc limit 1""")
            changetime = c.fetchone()[0]
            c.execute("""SELECT author, field, oldvalue, newvalue
                               from ticket_change where ticket = 4712
                               and time = ?""", [changetime])
            self.assertEqual(set(c.fetchall()),
                             set([('alice', 'summary',
                                   oldSummary, updateData['summary']),
                                  ('alice', 'comment',
                                   '20', ''),
                                  ('alice', 'owner',
                                   oldOwner, updateData['owner']),
                                  ('alice', 'keywords',
                                   oldKeywords, updateData['keywords']),
                                  ('alice', 'branch_author',
                                   oldBranchAuthor, updateData['branch_author'])]))
            c.execute("""SELECT value from ticket_custom
                         where ticket = 4712 and name = 'branch_author'""")
            self.assertEqual(c.fetchall(), [('bob',)])
        return d.addCallback(_checkDB)
    test_updateTicket.skip = "This needs authentication, first."
