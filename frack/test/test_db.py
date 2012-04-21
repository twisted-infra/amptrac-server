import sqlite3
from twisted.trial.unittest import TestCase
from twisted.python.util import sibpath
from frack.db import DBStore



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

        return d.addCallback(_check)
