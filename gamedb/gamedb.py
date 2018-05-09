import os
import re
import sqlite3


# This class represents a single subquery with inner join(s) when 
# a relation table is involved (many to many relation)
# This is designed specifically for 
# 'filter games' (MMR = many to many relations)
#
# table = external table that is linked into relation table (example: store)
# relation = relation table (example: gamesplat)
# op = operator (usually '=', but can be 'LIKE')
# data = the values to check (usually for table.name)
class _FilterGamesJoinMMR:
    def __init__(self, table, relation, op, data):
        if data is None:
            self.values = None
            return None
        self.relation = relation
        self.values = []
        for v in data:
            self.values.append(v.lower())
        self.joins = ['INNER JOIN {} ON {}.id = {}.{}id'.format(
                          table, table, relation, table
                         )]
        self.op = op
        self.where = []
        for value in self.values:
            self.where.append('lower({}.name) {} ?'.format(table, op))
        self.where = ' OR '.join(self.where)
        if len(data) > 1:
            self.where = '({})'.format(self.where)
    
    def __str__(self):
        if self.values is None:
            return ''
        else:
            return '''(SELECT gameid from {}
{}
WHERE {})'''.format(self.relation, self._printJoins(), self.where)
    
    def _printJoins(self):
        value = ''
        for index, j in enumerate(self.joins):
            if index > 0:
                value = value + '\n'
            value = value + j
        return value
    
    def update(self, other):
        if not isinstance(other, _FilterGamesJoinMMR):
            raise ValueError('other must be a _FilterGamesJoinMMR object')
        elif self.relation != other.relation:
            raise ValueError('{}{}({} != {})'.format(
                'cannot update _FilterGamesJoin:\n',
                'relations must be equal, but differs\n',
                self.relation, other.relation)
            )
        self.joins.append(other.joins[0])
        self.where = '{} AND {}'.format(self.where, other.where)
        self.values += other.values



class GameDB:    
    def __init__(self, dbname):
        self.conn = sqlite3.connect(dbname)
        self.cursor = self.conn.cursor()
        self._create_tables()
    
    def close(self):
        self.conn.close()
    
    # This function will create required tables (see "er" diagram for a
    #   complete list of the tables)
    def _create_tables(self):
        # This line will allow sqlite to check if a foreign key points
        # to an existing value or not
        self.cursor.execute("PRAGMA foreign_keys=ON")
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS subscription
            (id integer PRIMARY KEY AUTOINCREMENT, name text, icon text,
             d integer, m integer, y integer)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS game 
           (id integer PRIMARY KEY AUTOINCREMENT, title text, year integer,
            franchiseid integer, vote integer, priority integer,
            img text, note text,
            FOREIGN KEY(franchiseid) REFERENCES franchise(id)
           )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS platform 
           (id integer PRIMARY KEY AUTOINCREMENT, name text, device text, 
            icon text)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS store 
           (id integer PRIMARY KEY AUTOINCREMENT, name text, icon text)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS gamesplat
           (gameid integer, storeid integer, platformid integer, link text,
            subscriptionid integer,
            FOREIGN KEY(gameid) REFERENCES game(id),
            FOREIGN KEY(storeid) REFERENCES store(id),
            FOREIGN KEY(platformid) REFERENCES platform(id),
            FOREIGN KEY(subscriptionid) REFERENCES subscription(id),
            PRIMARY KEY(gameid, storeid, platformid))''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS tag 
            (id integer PRIMARY KEY AUTOINCREMENT, name text)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS gametag
           (gameid integer, tagid integer,
            FOREIGN KEY(gameid) REFERENCES game(id),
            FOREIGN KEY(tagid) REFERENCES tag(id),
            PRIMARY KEY(gameid, tagid))''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS franchise
            (id integer PRIMARY KEY AUTOINCREMENT, name text, img text)''')
        # self.cursor.execute("PRAGMA foreign_keys=ON")
        self.conn.commit()
        # if len(_list_tables) != N: <2>
        #     raise ValueError('database has more tables than expected')
    
    # this function will return the list of all the tables contained in the
    # database
    def _list_tables(self):
        tmp = self.cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table'""")
        tmp = tmp.fetchall()
        tables = [table[0] for table in tmp] 
        return [table for table in tables if 'sqlite' not in table]
    
    # internal function: adds an entry into 'game' table
    # see: add_game() function
    def _addgame_item(self, title, year=2000, franchise=None, vote=None, 
                 priority=6, img=None, note=None):
        self.cursor.execute(
            "INSERT INTO game VALUES (NULL, ?,?,?, ?,?,?, ?)",
            (title, year, franchise, vote, priority, img, note)
        )
        self.conn.commit()
    
    # add a platform (ps4, ps3, linux, win, ...) into 'platform' table
    # 'device' should be 'ps' for all playstations; 
    #          'pc' for 'win', 'linux', 'mac'
    def add_platform(self, name, device, icon=None):
        self.cursor.execute(
            "INSERT INTO platform VALUES (NULL, ?,?,?)",
            (name, device, icon)
        )
        self.conn.commit()
    
    # add a store (steam, uplay, gog) into 'store' table
    def add_store(self, name, icon=None):
        self.cursor.execute(
            "INSERT INTO store VALUES (NULL, ?,?)",
            (name, icon)
        )
        self.conn.commit()
    
    # add a tag (example: indie) into the 'tag' table
    # you can use only tags that are listed in the 'tag' table
    def add_tag(self, name):
        self.cursor.execute(
            "INSERT INTO tag VALUES (NULL,?)", (name,)
        )
        self.conn.commit()
    
    # add a franchise (example: "Assassin's Creed" for AC games)
    def add_franchise(self, name, img=None):
        self.cursor.execute(
            "INSERT INTO franchise VALUES (NULL,?,?)", (name,img)
        )
        self.conn.commit()
    
    # add a subscription for games that expires together with a subscription
    # for example: ps plus games will expires when ps+ subscription ends
    # d, m, y: those fields describe the date of subscription current expire
    #          date (d=day, m=month, y=year)
    def add_subscription(self, name, icon, d, m, y):
        self.cursor.execute(
            "INSERT INTO subscription VALUES (NULL,?,?, ?,?,?)", 
            (name, icon,  d, m, y)
        )
        self.conn.commit()
    
    # internal function: this will add an entry to the relational table
    # 'gamesplat'
    # see: add_game(); ER graphic
    def _addgamesplat(self, gameid, storeid, platformid, link=None, 
                      subscriptionid=None):
        self.cursor.execute(
            'INSERT OR IGNORE INTO gamesplat VALUES(?,?,?, ?,?)',
            (gameid, storeid, platformid, link, subscriptionid)
        )
    
    # internal function: this will add an entry to the relational table
    # 'gametag'
    # see: add_game(); ER graphic
    def _addgametag(self, gameid, tagid):
        self.cursor.execute(
            'INSERT OR IGNORE INTO gametag VALUES(?,?)',
            (gameid, tagid)
        )
    
    # internal function: this will return None or an id (int value)
    # this function should never be used outside GameDB class
    def _sid(self, table, param, value):
        if value is None:
            return None
        myval = self.cursor.execute(
                "SELECT id FROM {} WHERE lower({})=?".format(table, param), 
                (value.lower(),)
        )
        myval = myval.fetchall()
        if len(myval) == 0:
            return None
        else:
            return myval[0][0]
    
    # Add a game from a single csv entry.
    # subscription, tag, franchise, store, platform must exists
    # so you cannot use, for example, a store not listed in 'store' table
    # note: subscription, franchise and tag can be an empty value
    #
    # add_game will:
    # - add the game in the game table (calling _addgame_item)
    # - add gamesplat relation (calling _addgamesplat)
    # - add gametag relation if a non-empty tag is provided (_addgametag)
    def add_game(self, subscription, priority, title, tag, franchise,
                    year, vote, img, lang, store, platform, link, note):
        # from the csv entry we have 'real' values 
        #      (subscription.name, franchise.name ...)
        # but _addgame_item will need ids (franchiseid, platid) so we
        # callect all the ids we will require
        franchiseid = self._sid('franchise', 'name', franchise)
        platid = self._sid('platform', 'name', platform)
        storeid = self._sid('store', 'name', store)
        tagid = self._sid('tag', 'name', tag)
        subsid = self._sid('subscription', 'name', subscription)
        for xid, tab, xname in [(platid, 'platform', platform), 
                                (storeid, 'store', store),
                                (tagid, 'tag', tag),
                                (subsid, 'subscription', subscription)]:
            if xid is None and xname is not None:
                raise ValueError('{} "{}" not found in database'.format(
                    tab, xname)
                )
            if tab in ('platform', 'store') and xname is None:
                raise ValueError(
                    'Unexpected None value for {}\n'
                    'Matched on title {}'.format(tab, title)
                )
        gid = self._sid('game', 'title', title)
        # we add a game entry in 'game' table only if it still does not exist
        if gid is None:
            self._addgame_item(title, year, franchiseid, vote, 
                               priority, img, note)
            gid = self._sid('game', 'title', title)
        self._addgamesplat(gid, storeid, platid, link, subsid)
        self._addgametag(gid, tagid)
    
    def searchgame(self, title):
        myval = self.cursor.execute(
            'SELECT * FROM game WHERE title=?', (title,))
        return myval.fetchall()
    
    def searchplat(self, name):
        myval = self.cursor.execute(
            'SELECT * FROM platform WHERE name=?', (name,))
        return myval.fetchall()
    
    # filter ga,es query
    def _fgquery(self, *, title=None, tag=None, platform=None,
                     store=None, franchise=None, page=1):
        args = [title, tag, platform, store, franchise]
        query = 'SELECT id, title, vote, priority, img FROM game'
        query_segments = []
        if not all(var is None for var in args):
            query = query + ' WHERE '
        injoins = {}
        values = []
        for table, relation, op, data in [
                   ('tag', 'gametag', '=', tag),
                   ('platform', 'gamesplat', '=', platform),
                   ('store', 'gamesplat', '=', store)]:
            if data is None:
                continue
            injoin_candidate = _FilterGamesJoinMMR(table, relation, op, data)
            if relation in injoins:
                injoins[relation].update(injoin_candidate)
            else:
                injoins[relation] = injoin_candidate
        offset = ''
        if page > 1:
            offset = ' OFFSET {}'.format(30 * (page -1))
        if title is not None:
            query_segments.append('lower(title) LIKE ?')
            values.append('%{}%'.format(title.lower()))
        if franchise is not None:
            query_segments.append(
                'franchiseid IN\n'
                '(SELECT franchise.id FROM franchise WHERE '
                'franchise.name LIKE ?)'
            )
            values.append('%{}%'.format(franchise.lower()))
        for j in injoins.values():
            query_segments.append( 'id IN\n{}'.format(str(j)) )
            values += j.values
        query = query + '\nAND '.join(query_segments)
        query = query + '\nORDER BY title LIMIT 30{}'.format(offset)
        query = query.strip()
        return (query, values)
    
    def filter_games(self, *, title=None, tag=None, platform=None,
                     store=None, franchise=None, page=1):
        # franchise is not yet supported, this is why we set it to None
        query, values = self._fgquery(
                title=title, tag=tag, platform=platform,
                store=store, franchise=franchise, page=page
        )
        result = self.cursor.execute(query, values)
        result = result.fetchall()
        return result
        
        
        
    
    def todo(self):
        pass