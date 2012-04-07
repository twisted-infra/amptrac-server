# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.
from twisted.internet import defer

def connect_or_else(name):
    try:
        import pgdb
    except ImportError:
        try:
            import psycopg2
        except ImportError:
            from pg8000 import pg8000_dbapi
            con = pg8000_dbapi.connect(host='localhost', database=name)
        else:
            con = psycopg2.connect("host=/tmp dbname=" + name)
    else:
        con = pgdb.connect("127.0.0.1:" + name)
    return con


class DBStore(object):
    def __init__(self, name):
        self.name = name
        self.connection = connect_or_else(name)


    def fetchTicket(self, ticketNumber):
        c = self.connection.cursor()
        c.execute(
            "SELECT id, type, time, component, priority, owner, reporter, "
            "cc, status, resolution, summary, description, keywords "
            "FROM ticket WHERE id = %s", [ticketNumber])
        ticketRow = c.fetchone()
        c.execute("SELECT time, author, field, oldvalue, newvalue "
                    "FROM ticket_change WHERE ticket = %s ORDER BY time",
                    [ticketNumber])
        changeFields = ['time', 'author', 'field', 'oldvalue', 'newvalue']
        ticketFields = ["id", "type", "time", "component", "priority", "owner",
                        "reporter", "cc", "status", "resolution", "summary",
                        "description", "keywords"]
        changesRow = c.fetchall()
        ticket = dict([(k, v or '') for k, v in zip(ticketFields, ticketRow)])
        ticket['changes'] = []
        for change in changesRow:
            ticket['changes'].append(dict([(k, v or '') for k, v in zip(changeFields, change)]))
        return defer.succeed(ticket)
