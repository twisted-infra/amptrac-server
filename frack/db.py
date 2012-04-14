# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.
from twisted.internet import defer

def postgres_probably_connect(name, username):
    try:
        import pgdb
    except ImportError:
        try:
            import psycopg2
        except ImportError:
            from pg8000 import pg8000_dbapi
            module = pg8000_dbapi
            con = pg8000_dbapi.connect(username, host='localhost', database=name)
        else:
            module = psycopg2
            con = psycopg2.connect(host="/tmp", dbname=name,  user=username)
    else:
        module = pgdb
        con = pgdb.connect(host="127.0.0.1", database=name, user=username)
    return module, con


def sqlite_connect(path):
    import sqlite3
    return sqlite3, sqlite3.connect(path)


class DBStore(object):
    def __init__(self, connection):
        module, self.connection = connection
        if module.paramstyle == 'qmark':
            self.pl = '?'
        else:
            self.pl = '%s'

    def q(self, query):
        return query.replace('?', self.pl)

    def fetchTicket(self, ticketNumber):
        c = self.connection.cursor()
        c.execute(self.q(
                "SELECT id, type, time, component, priority, owner, reporter, "
                "cc, status, resolution, summary, description, keywords "
                "FROM ticket WHERE id = ?"), [ticketNumber])
        ticketRow = c.fetchone()
        c.execute(self.q("SELECT time, author, field, oldvalue, newvalue "
                         "FROM ticket_change WHERE ticket = ? ORDER BY time"),
                  [ticketNumber])
        changeFields = ['time', 'author', 'field', 'oldvalue', 'newvalue']
        ticketFields = ["id", "type", "time", "component", "priority", "owner",
                        "reporter", "cc", "status", "resolution", "summary",
                        "description", "keywords"]
        changesRow = c.fetchall()
        ticket = dict([(k, v or '') for k, v in zip(ticketFields, ticketRow)])

        c.execute(self.q("SELECT name, value from ticket_custom where name "
                         "in ('branch', 'branch_author', 'launchpad_bug') "
                         "and ticket = ?"),
                  [ticketNumber])
        ticket.update(c.fetchall())
        ticket['attachments'] = []
        ticket['changes'] = []
        for change in changesRow:
            ticket['changes'].append(dict([(k, v or '') for k, v in zip(changeFields, change)]))
        return defer.succeed(ticket)
