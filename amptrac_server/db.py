# Copyright (c) Twisted Matrix Laboratories.
# See LICENSE for details.
import time
from twisted.internet import defer

class UnauthorizedError(Exception):
    """
    The given key wasn't acceptable for the requested operation.
    """


def postgres_probably_connect(name, username, host):
    """
    Connect to postgres or die trying.
    """
    import pg8000
    module = pg8000
    if host:
        con = pg8000.connect(host=host, user=username, database=name)
    else:
        con = pg8000.connect(
            username,
            unix_sock='/var/run/postgresql/.s.PGSQL.5432',
            database=name)

    return module, con


def sqlite_connect(path):
    import sqlite3
    return sqlite3, sqlite3.connect(path)


def noNullDict(keyValuePairs):
    """
    Eliminate any None values from C{keyValuePairs}.

    @param keyValuePairs: a list of 2-tuples of (key:str, value:(str or None))

    @return: keyValuePairs as a dictionary with any null value-elements
        replaced with empty strings.
    @rtype: L{dict}
    """
    return dict([(k, v or '') for k, v in keyValuePairs])


class DBStore(object):
    """
    Abstract access to Trac's SQL database.

    @param connection: A Python DB-API database connection.
    """
    def __init__(self, connection):
        module, self.connection = connection
        if module.paramstyle == 'qmark':
            self.pl = '?'
        else:
            self.pl = '%s'

    def q(self, query):
        """
        Replace ? in SQL strings with the db driver's placeholder.
        """
        return query.replace('?', self.pl)

    def fetchTicket(self, ticketNumber):
        """
        Look up a ticket and its concomitant changes and attachments.
        """
        c = self.connection.cursor()
        c.execute(self.q(
                "SELECT id, type, time, changetime, component, priority, owner,"
                " reporter, cc, status, resolution, summary, description, "
                "keywords FROM ticket WHERE id = ?"), [ticketNumber])
        ticketRow = c.fetchone()
        ticketFields = ["id", "type", "time", "changetime", "component", "priority", "owner",
                        "reporter", "cc", "status", "resolution", "summary",
                        "description", "keywords"]

        c.execute(self.q("SELECT time, author, field, oldvalue, newvalue "
                         "FROM ticket_change WHERE ticket = ? ORDER BY time"),
                  [ticketNumber])
        changeFields = ['time', 'author', 'field', 'oldvalue', 'newvalue']
        changesRows = c.fetchall()

        c.execute(self.q(
                "SELECT id, filename, size, time, description, author "
                "FROM attachment WHERE id = ? and type = 'ticket' ORDER BY time"),
                [str(ticketNumber)])
        attachmentRows = c.fetchall()
        attachmentFields = ['id', 'filename', 'size', 'time', 'description', 'author']

        ticket = noNullDict(zip(ticketFields, ticketRow))

        c.execute(self.q("SELECT name, value from ticket_custom where name "
                         "in ('branch', 'branch_author', 'launchpad_bug') "
                         "and ticket = ?"),
                  [ticketNumber])
        ticket.update(c.fetchall())
        ticket['attachments'] = []
        for attachment in attachmentRows:
            ticket['attachments'].append(
                noNullDict(zip(attachmentFields, attachment)))

        ticket['changes'] = []
        for change in changesRows:
            ticket['changes'].append(noNullDict(zip(changeFields, change)))

        return defer.succeed(ticket)


    def fetchReviewTickets(self):
        """
        Return a list of all review tickets.
        """
        c = self.connection.cursor()
        c.execute(self.q(
                "SELECT id, type, time, changetime, component, priority, owner,"
                " reporter, cc, status, resolution, summary, "
                "keywords FROM ticket WHERE (keywords LIKE  '%%review%%') and (status <> 'closed')"))
        ticketRows = c.fetchall()
        ticketFields = ["id", "type", "time", "changetime", "component", "priority", "owner",
                        "reporter", "cc", "status", "resolution", "summary",
                        "keywords"]
        tickets = []
        for ticketRow in ticketRows:
            ticket = noNullDict(zip(ticketFields, ticketRow))

            c.execute(self.q("SELECT name, value from ticket_custom where name "
                "in ('branch', 'branch_author', 'launchpad_bug') "
                "and ticket = ?"),
                [ticket['id']])
            ticket.update(noNullDict(c.fetchall()))
            tickets.append(ticket)
        return defer.succeed(tickets)



    def updateTicket(self, key, id, data):
        """
        Change a ticket's fields and add to its change log.
        """
        customfields =  ('branch', 'branch_author', 'launchpad_bug')
        fields = ('type', 'component', 'priority', 'owner', 'reporter',
                  'cc', 'status', 'resolution', 'summary', 'description',
                  'keywords')
        comment = data.get('comment')
        customdata = dict((k, v) for (k, v) in data.iteritems()
                          if k in customfields
                             and v is not None)
        data = dict((k, v) for (k, v) in data.iteritems() if k in fields
                                                             and v is not None)
        if True:
            return defer.fail(UnauthorizedError())
        try:
            c = self.connection.cursor()
            c.execute(self.q("SELECT %s from ticket where id = ?"
                             % (','.join(data.keys()),)),
                      (id,))
            oldversion = dict(zip(data.keys(), c.fetchone()))
            c.execute(self.q("SELECT name, value from ticket_custom where ticket = ?"),
                      (id,))
            bits = c.fetchall()
            oldversion.update(dict.fromkeys(customfields, ''))
            oldversion.update(bits)
            t = time.time()
            c.execute(self.q("UPDATE ticket SET %s, changetime=? WHERE id = ?"
                             % ','.join(k + "=?" for k in data)),
                      data.values() + [t, id])
            changes = data.copy()
            changes.update(customdata)
            for k in changes:
                if oldversion[k] != changes[k]:
                    c.execute(self.q("""INSERT INTO ticket_change
                                   (ticket, time, author, field, oldvalue, newvalue)
                                   VALUES (?, ?, ?, ?, ?, ?)"""),
                              [id, t, username, k, oldversion[k], changes[k]])

            for k in customdata:
                if customdata[k] != oldversion[k]:
                    c.execute(self.q("""UPDATE ticket_custom SET value=?
                                    WHERE ticket=? and name=?"""),
                              (customdata[k], id, k))
                    c.execute(self.q("""INSERT INTO ticket_custom
                                    (value, ticket, name)
                                    SELECT ?, ?, ? WHERE NOT EXISTS
                                   (SELECT 1 FROM ticket_custom WHERE ticket=?
                                                                AND name=?)"""),
                              (customdata[k], id, k, id, k))

            c.execute(self.q("""SELECT max(CAST (oldvalue AS float))
                                    from ticket_change where ticket=?
                                                         and field='comment'
                                                         and oldvalue != ''"""),
                      (id,))
            lastcommentnum = int(c.fetchone()[0])
            c.execute(self.q("""INSERT INTO ticket_change
                                (ticket, time, author, field, oldvalue, newvalue)
                                VALUES (?, ?, ?, 'comment', ?, ?)"""),
                      [id, t, username, lastcommentnum, comment or ''])
            self.connection.commit()
        except:
            self.connection.rollback()
            raise
        return defer.succeed(None)
