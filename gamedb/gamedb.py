import os
import re
import sqlite3
from gamedb.gameview import GameView
from gamedb.gamedberr import *


#---------------------
# Generate an ItemExistsError
#---------------------
def _item_added_error(gamedb, e, table, params, m):
    # gamedb: gamedb object
    # e: original sqlite.IntegrityError exception.
    # table: sqlite3 table where exception happened.
    # params: params passed to GameDB that caused the sqlite3 exception.
    # m: regexp match -> regexp = "UNIQUE constraint failed\: (.*)"
    # ---------
    # First we capture from m (regexp match) the values of
    # table1.colum1, table2.colum2... (storing them in a string)
    unique_failed = m.group(1)
    # profile is a dictionary that contains all combinations for 
    # unique_colums_org related to table that can raise ItemExistsError.
    # those 'combinations' are stored as tuple:
    # index 0: unique_costraint_failed message from sqlite3.IntegrityError
    # index 1: tuple containing the indexes for 'params' related to that
    #          unique costraint
    # example: 'tag.name' is the second parameter (index 1) passed with an
    #          add_item('tagname') becouse add_item will silently add a NULL
    #          value when trying to add a new tag (autoincremental ID in tag) 
    profile = {
        'gametag': ('gametag.gameid, gametag.tagid', (0, 1)),
        'gamesplat': (
            'gamesplat.gameid, gamesplat.storeid, gamesplat.platformid',
            (0, 1, 2)),
        'tag': ('tag.name', (1,)),
        'franchise': ('franchise.name', (1,)),
        'platform': ('platform.name', (1,)),
        'store': ('store.name', (1,)),
        'subscription': ('subscription.name', (1,)),
        'splatgroup': ('splatgroup.name', (1,))
    }
    if unique_failed != profile[table][0]:
        return UnexpectedError(
            'Found an unexpected (unlisted) sqlite3.IntegrityError with an '
            '"Unique costraint failed" when trying to generate an '
            'ItemExistsError exception.\n'
            'Sqlite original error message was "{}".'
            'Please open a bug report if you encountered this '
            'error message.'.format(e.args[0])
        )
    # now we get the colums names from profile and put them in a list
    columns = profile[table][0].split(', ')
    # and we get parameters we actually need
    pars = [params[i] for i in profile[table][1]]
    # we 'hack' values in gametag and gamesplat in order to have game.title, etc
    # instead of ids
    if table in ('gametag', 'gamesplat'):
        columns = ('game.title', 'store.name', 'platform.name')
        if table == 'gametag':
            columns = ('game.title', 'tag.name')
        pars2 = []
        for column, xid in zip(columns, pars):
            tab, col = column.split('.')
            val = gamedb.cursor.execute(
                'SELECT {} FROM {} WHERE id=?'.format(col, tab),
                (xid,)
            )
            val = val.fetchall()
            pars2.append(val[0][0])
        pars = pars2
    # finally we pair colums, pars in 'values'
    values = [(x, y) for x, y in zip(columns, pars)]
    if table in ('gametag', 'gamesplat'):
        return RelationExistsError(table, values)
    return ItemExistsError(table, values)



#---------------------
# Generate:
#   - x
#   - y
#  from sqlite3.OperationalError
#---------------------
def _sqlite_operr(e, table, params):
    m1 = re.match('table (\S+) has ([0-9]+) columns but ([0-9]+)', e.args[0])
    if m1:
        table = m1.group(1)
        if table == 'splatgroup':
            table = 'group'
        return ItemError.fromWrongNumpars(table, int(m1.group(2)), 
                                          int(m1.group(3)))
    else:
        return e



#---------------------
# Class the represents a single subquery with inner join(s)
#
# This class is designed specifically for GameDB.filter games
# (MMR = many to many relations)
#
# This class is an internal class and you don't require to use it outside gamedb
# module
#---------------------
class _FilterGamesJoinMMR:
    def __init__(self, table, relation, op, data):
        # ----
        # initialize _FilterGamesJoinMMR
        # params:
        # table (string) = table name (example: store)
        # relation (string) = relation table (example: gamesplat)
        # op (string) = operator (usually '=', but can be 'LIKE')
        # data (list of strings) = the values to check (usually for table.name)
        # ----
        if data is None:
            self.values = None
            return None
        self.relation = relation
        self.values = [x.lower() for x in data]
        self.joins = ['INNER JOIN {} ON {}.id = {}.{}id'.format(
                          table, table, relation, table
                         )]
        self.op = op
        self.where = [
            'lower({}.name) {} ?'.format(table, op) for x in self.values
        ]
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
        # String convertion (to allow to print the subquery)
        value = ''
        for index, j in enumerate(self.joins):
            if index > 0:
                value = value + '\n'
            value = value + j
        return value
    
    def update(self, other):
        # Updates _FilterGamesJoinMMR with data contained into another
        # _FilterGamesJoinMMR object. Relation tables must be the same
        if not isinstance(other, _FilterGamesJoinMMR):
            raise ValueError('other must be a _FilterGamesJoinMMR object')
        elif self.relation != other.relation:
            raise ValueError(
                'cannot update _FilterGamesJoin:\n'
                'relations must be equal, but differs\n'
                '({} != {})'.format(self.relation, other.relation)
            )
        self.joins.append(other.joins[0])
        self.where += ' AND {}'.format(other.where)
        self.values += other.values



'''
Class that manages all database operations for games.db
'''
class GameDB:
    def __init__(self, dbname):
        '''Intialize database (database_file)'''
        self.conn = sqlite3.connect(dbname)
        self.cursor = self.conn.cursor()
        self._create_tables()
        self.tables = self._list_tables()
    
    def close(self):
        '''close database connection'''
        self.conn.close()
    
    # This function will create required tables (see "er" diagram for a
    #   complete list of the tables)
    def _create_tables(self):
        # This line will allow sqlite to check if a foreign key points
        # to an existing value or not
        self.cursor.execute("PRAGMA foreign_keys=ON")
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS subscription
            (id integer PRIMARY KEY AUTOINCREMENT, name text UNIQUE NOT NULL, 
             icon text, d integer, m integer, y integer)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS game 
           (id integer PRIMARY KEY AUTOINCREMENT, title text NOT NULL, 
            year integer, franchiseid integer, vote integer, priority integer,
            img text, note text,
            FOREIGN KEY(franchiseid) REFERENCES franchise(id)
           )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS platform 
           (id integer PRIMARY KEY AUTOINCREMENT, name text UNIQUE NOT NULL,
            icon text, splatgroupid integer,
            FOREIGN KEY(splatgroupid) REFERENCES splatgroup(id)
           )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS store 
           (id integer PRIMARY KEY AUTOINCREMENT, name text UNIQUE NOT NULL, 
            icon text, splatgroupid integer,
            FOREIGN KEY(splatgroupid) REFERENCES splatgroup(id))''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS gamesplat
           (gameid integer, storeid integer, platformid integer, 
            lang text, link text, subscriptionid integer, isdemo integer,
            FOREIGN KEY(gameid) REFERENCES game(id),
            FOREIGN KEY(storeid) REFERENCES store(id),
            FOREIGN KEY(platformid) REFERENCES platform(id),
            FOREIGN KEY(subscriptionid) REFERENCES subscription(id),
            PRIMARY KEY(gameid, storeid, platformid))''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS tag 
            (id integer PRIMARY KEY AUTOINCREMENT, 
             name text UNIQUE NOT NULL)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS gametag
           (gameid integer, tagid integer,
            FOREIGN KEY(gameid) REFERENCES game(id),
            FOREIGN KEY(tagid) REFERENCES tag(id),
            PRIMARY KEY(gameid, tagid))''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS franchise
            (id integer PRIMARY KEY AUTOINCREMENT, 
            name text UNIQUE NOT NULL, img text)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS splatgroup
            (id integer PRIMARY KEY AUTOINCREMENT, 
             name text UNIQUE NOT NULL)''')
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
    
    def list_items(self, table):
        ''' returns a dictionary where key=item_name, value=item_id '''
        if table == 'group':
            table = 'splatgroup'
        elif table not in self.tables:
            raise ValueError('invalid table')
        elif table in ('gamesplat', 'gametag'):
            raise ValueError(
                'cannot list items from table "{}", wich is a relation '
                'table'.format(table))
        name = 'title' if table == 'game' else 'name'
        val = self.cursor.execute('SELECT {}, id from {}'.format(name, table))
        val = dict(val.fetchall())
        return val
    
    def add_item(self, table, params):
        ''' add a value in a table
        
        add_item should not be used directly for tables 'game', 
        'gametag', 'gamesplat', becouse those tables should be
        managed by add_game when adding game with relations        
        '''
        
        # s = string; i = integer;
        # profile_check is generated by test_gamedb.py when function 
        # disabled_test_create_additem_profilecheck(self)
        # is renamed removing 'disabled_' from function name
        # some minor manual fixes were needed for this final result:
        # (for example store, platform require a groupid integer, but here 
        #  string will be accepted since the code will convert the string into
        #  the id)
        profile_check = {
            'subscription': (
                ('name', 's'), ('icon', 's'), 
                ('d', 'i'), ('m', 'i'), ('y', 'i')),
            'game': (
                ('title', 's'), ('year', 'i'), ('franchiseid', 'i'), 
                ('vote', 'i'), ('priority', 'i'), ('img', 's'), ('note', 's')),
            'platform': (
                ('name', 's'), ('icon', 's'), ('splatgroupid', 's')),
            'store': (
                ('name', 's'), ('icon', 's'), ('splatgroupid', 's')),
            'gamesplat': (
                ('gameid', 'i'), ('storeid', 'i'), ('platformid', 'i'), 
                ('lang', 's'), ('link', 's'), 
                ('subscriptionid', 'i'), ('isdemo', 'i')),
            'tag': (('name', 's'),),
            'gametag': (('gameid', 'i'), ('tagid', 'i')),
            'franchise': (('name', 's'), ('img', 's')),
            'group': (('name', 's'),),
            'splatgroup': (('name', 's'),)
        }
        checks = profile_check[table]
        # type checks: we will do them only if number of params are right.
        # Else, we will ignore type check (an error for wrong number of 
        # parameters will be raised later
        if len(checks) == len(params):
            for param, check in zip(params, checks):
                # we will ignore NULL params. If a None value is passed into a
                # NON NULL column, an ItemError will be raised later
                if param is None:
                    continue
                # check[1] contains expected type for column ('i' or 's')
                # check[0] contains the column name
                if check[1] == 'i' and not isinstance(param, int):
                    raise ItemError.fromType(
                        table, check[0], 'int', 'string')
                elif check[1] == 's' and not isinstance(param, str):
                    raise ItemError.fromType(
                        table, check[0], 'string', 'int')
        sgrp = None
        if table in ('store', 'platform'):
            if params[2] is not None:
                sgrp = self._sid('splatgroup', 'name', params[2])
                if sgrp is None:
                    raise ItemRequiredError(table, params[0],
                                            'group', params[2])
            if len(params) != 3:
                raise ItemError.fromWrongNumpars(table, 3, len(params))
            t1, t2, _ = params
            params = (None, t1, t2, sgrp)
        elif table in ('game', 'tag', 'franchise', 
                       'splatgroup', 'group', 'subscription'):
            if table == 'group':
                table = 'splatgroup'
            params = (None, *params)
        elif table not in ('gametag', 'gamesplat'):
            raise UnexpectedError(
                'insert error: unvalid table: {}'.format(table)
            )
        try:
            self.cursor.execute(
                "insert INTO {} VALUES ({})".format(
                    table, ','.join('?' for x in params)
                ), params
            )
        except sqlite3.IntegrityError as e:
            m1 = re.match(r'UNIQUE constraint failed\: (.*)', 
                            e.args[0])
            m2 = re.match(r'NOT NULL constraint failed: (.*)',
                            e.args[0])
            if m1:
                raise _item_added_error(self, e, table, params, m1) from None
            elif m2:
                raise ItemError(
                    'Unexpected NULL value: {}'.format(m2.group(1))
                ) from None
            else:
                raise e from None
        except sqlite3.OperationalError as e:
            raise _sqlite_operr(e, table, params) from None
    # internal function: adds an entry into 'game' table
    # see: add_game() function
    def _addgame_item(self, title, year=2000, franchise=None, vote=None, 
                 priority=6, img=None, note=None):
        self.cursor.execute(
            "INSERT INTO game VALUES (NULL, ?,?,?, ?,?,?, ?)",
            (title, year, franchise, vote, priority, img, note)
        )
    
    def add_platform(self, name, icon=None, group=None):
        '''add a platform (ps4, ps3, linux, win, ...) into 'platform' table
    
        'device' should be 'ps' for all playstations; 
        'device' = 'pc' for the following platforms: 'win', 'linux', 'mac'
        '''
        self.cursor.execute(
            "INSERT INTO platform VALUES (NULL, ?,?,?)",
            (name, icon, group)
        )
    
    def add_store(self, name, icon=None, group=None):
        '''add a store (steam, uplay, gog) into 'store' table'''
        self.cursor.execute(
            "INSERT INTO store VALUES (NULL, ?,?,?)",
            (name, icon, group)
        )
    
    def add_tag(self, name):
        ''' add a tag (example: indie) into the 'tag' table
        
        You must add_tag(x) before trying to add a game with tag 'x'
        '''
        self.cursor.execute(
            "INSERT INTO tag VALUES (NULL,?)", (name,)
        )
    
    def add_group(self, name):
        ''' add a group for store or platform (or both gh) (example: "PC")
        
        You must add_group(x) before trying to use a group in stores
        '''
        self.cursor.execute(
            "INSERT INTO splatgroup VALUES (NULL,?)", (name,)
        )
    
    def add_franchise(self, name, img=None):
        '''add a franchise (example: "Assassin's Creed" for AC games)'''
        self.cursor.execute(
            "INSERT INTO franchise VALUES (NULL,?,?)", (name,img)
        )
    
    def add_subscription(self, name, icon, d, m, y):
        '''
        add a subscription for games that expires together with a subscription
        
        for example: ps plus games will expires when ps+ subscription ends
        d, m, y: those fields describe the date when subscription will expire
        (d=day, m=month, y=year)
        '''
        self.cursor.execute(
            "INSERT INTO subscription VALUES (NULL,?,?, ?,?,?)", 
            (name, icon,  d, m, y)
        )
    
    # internal function: this will add an entry to the relational table
    # 'gamesplat'
    # see: add_game(); ER graphic
    def _addgamesplat(self, gameid, storeid, platformid, lang='en', link=None, 
                      subscriptionid=None, isdemo=False):
        self.cursor.execute(
            'INSERT OR IGNORE INTO gamesplat VALUES(?,?,?, ?,?,?, ?)',
            (gameid, storeid, platformid, lang, link, subscriptionid,
             int(isdemo))
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
        if table == 'game' and param == 'name':
            param = 'title'
        myval = self.cursor.execute(
                "SELECT id FROM {} WHERE lower({})=?".format(table, param), 
                (value.lower(),)
        )
        myval = myval.fetchall()
        if myval:
            return myval[0][0]
    
    # internal function: returns a value from id (the opposite of _sid)
    def _sval(self, table, param, xid):
        if table == 'game' and param == 'name':
            param = 'title'
        myval = self.cursor.execute(
            'SELECT {} FROM {} WHERE id=?'.format(param, table),
            (xid,)
        )
        myval = myval.fetchall()
        if myval:
            return myval[0][0]
    
    def add_game(self, subscription, priority, title, tag, franchise,
                    year, vote, img, lang, store, platform, link, note, *,
                    isdemo=False):
        '''
        Add a game from a single csv entry.
        subscription, tag, franchise, store, platform must exists
        so you cannot use, for example, a store not listed in 'store' table
        note: subscription, franchise and tag can be an empty value
        
        add_game will:
        - add the game in the game table
        - add gamesplat relation
        - add gametag relation if a non-empty tag is provided
        
        from the csv entry we will 'real' values 
          (subscription.name, franchise.name ...)
        '''
        # add_game will use _addgame_item to add the game in game table
        # but _addgame_item will need ids (franchiseid, platid) so we
        # callect all the ids we will require
        franchiseid = self._sid('franchise', 'name', franchise)
        platid = self._sid('platform', 'name', platform)
        storeid = self._sid('store', 'name', store)
        tagid = self._sid('tag', 'name', tag)
        subsid = self._sid('subscription', 'name', subscription)
        for table, val, xid in [
                ('franchise', franchise, franchiseid), 
                ('platform', platform, platid),
                ('store', store, storeid),
                ('tag', tag, tagid),
                ('subscription', subscription, subsid)]:
            if xid is None and val is not None:
                raise ItemRequiredError(
                    'game', title, table, val)
        for xid, tab, xname in [(platid, 'platform', platform), 
                                (storeid, 'store', store),
                                (tagid, 'tag', tag),
                                (subsid, 'subscription', subscription)]:
            if xid is None and xname is not None:
                raise ItemRequiredError('game', title, tab, xname)
            if tab in ('platform', 'store') and xname is None:
                raise GameError(
                    'Unexpected None value for {}\n'
                    'Matched on title {}'.format(tab, title)
                )
        gid = self._sid('game', 'title', title)
        # we add a game entry in 'game' table only if it still does not exist
        if gid is None:
            self.add_item('game',
                (title, year, franchiseid, vote, priority, img, note))
            gid = self._sid('game', 'title', title)
        try:
            self.add_item('gametag', (gid, tagid))
        except RelationExistsError:
            pass
        try:
            self.add_item('gamesplat', 
                (gid, storeid, platid, lang, link, subsid, int(isdemo)))
        except RelationExistsError:
            # when gamesplat relation already exists, usually ignore the new
            # entry. BUT: if the new entry IS NOT a demo AND the old entry
            # was a demo, then the new entry will replace the old one.
            if isdemo is True:
                return
            wasdemo = self.cursor.execute(
                '''SELECT isdemo FROM gamesplat WHERE gameid=? AND 
                storeid=? AND platformid=?''', (gid, storeid, platid))
            wasdemo = wasdemo.fetchall()
            wasdemo = bool(wasdemo[0][0])
            if wasdemo is False:
                return
            self.cursor.execute(
                'REPLACE INTO gamesplat VALUES (?,?,?,?, ?,?,?)',
                (gid, storeid, platid, lang, link, subsid, int(False)))
    
    def searchgame(self, title):
        '''this function may be removed in a future'''
        myval = self.cursor.execute(
            'SELECT * FROM game WHERE title=?', (title,))
        return myval.fetchall()
    
    def searchplat(self, name):
        '''this function may be removed in a future'''
        myval = self.cursor.execute(
            'SELECT * FROM platform WHERE name=?', (name,))
        return myval.fetchall()
    
    # calculate and return query, values for GameDB.filter_games
    def _fgquery(self, *, title=None, tags=None, platforms=None,
                     stores=None, franchise=None, page=1, 
                     sortby='title', limit=30):
        args = [title, tags, platforms, stores, franchise]
        query = 'SELECT id, title, vote, priority, img FROM game'
        query_segments = []
        if not all(var is None for var in args):
            query += ' WHERE '
        injoins = {}
        values = []
        for table, relation, op, data in [
                   ('tag', 'gametag', '=', tags),
                   ('platform', 'gamesplat', '=', platforms),
                   ('store', 'gamesplat', '=', stores)]:
            if data is None:
                continue
            injoin_candidate = _FilterGamesJoinMMR(table, relation, op, data)
            if relation in injoins:
                injoins[relation].update(injoin_candidate)
            else:
                injoins[relation] = injoin_candidate
        if isinstance(limit, int) and limit > 1:
            limit_str = 'LIMIT {}'.format(limit)
        else:
            limit_str = ''
        offset = ''
        if page > 1 and limit_str != '':
            offset = 'OFFSET {}'.format(limit * (page -1))
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
        query += '\nAND '.join(query_segments)
        query += '\nORDER BY {} {} {}'.format(sortby, limit_str, offset)
        query = query.strip()
        return (query, values)
    
    def filter_games(self, *, title=None, tags=None, platforms=None,
                     stores=None, franchise=None, page=1, sortby='title',
                     count_total=False, limit=30):
        '''return tuple: (filtered list of games, total_games_found)
        
        Almost every parameter is a filter that can be asked (or not) by user
        title (string): title of game to search
        tags (list): list of tags (*)
        platforms (list): list of platforms (*)
        stores (list): list of stores (*)
        franchise (string): franchise name to search
        page (int): search page (useful when total games listed > 30)
        count_total (bool): if True the second argument of the returned tuple 
        value will contain total games found. If false the second argument
        returned will be None. By default count_total is False
        All those values (except page and count_total) can be None if a filter 
        is NOT asked.
        
        The first value returned by this function will be a list of tuples. 
        Every tuple will contain:
        (id, title, vote, priority, img) where:
        id (integer)        = game ID
        title (string)      = game title
        vote (int/None)     = game metacritic vote (0 to 100)
        priority (int/None) = game priority 'vote' (0 to 10)
        img (string)        = game image file name
        
        The second value depends of count_total setting. If count_total is
        False the second value will be None. Otherwhise it is the number of
        total games found with that filter
        
        Notes:
        (*) Must be a list even if only one item must be checked. So you need
        to use a list of one element only if you need to search only one item.
        '''
        if sortby not in ('title', 'priority', 'vote'):
            raise ValueError(
                'sortby can be only "title", "priority" or "vote"'
            )
        elif sortby != 'title':
            sortby += ' DESC'
        query, values = self._fgquery(
                title=title, tags=tags, platforms=platforms,
                stores=stores, franchise=franchise, page=page,
                sortby=sortby, limit=limit
        )
        result = self.cursor.execute(query, values)
        result = result.fetchall()
        if not count_total:
            return (result, None)
        query2 = re.sub(r'ORDER BY.*', '', query)
        query2 = 'SELECT count(*) FROM ({})'.format(query2)
        count = self.cursor.execute(query2, values)
        count = count.fetchall()
        count = count[0][0]
        return (result, count)
    
    def gameview(self, gameid, *, view='name'):
        '''This function will return details for a single game (GameView)
        
        Some informations contained in the GameView object returned by 
        this function will be different if view='name' or view='icon'
        By default 'store', 'franchise' and 'subscription' sub-parameters of
        GameView object will contain its name (view='name')
        It is possible to use view='icon' to store icon file names instead.
        All other GameView subparameters will not depend of 'view' type.
        
        For other informations about object returned by this function, please
        see GameView class
        '''
        if view not in ('name', 'icon'):
            raise ValueError("view legal values are only 'name' or 'icon'")
        storeplats = self.cursor.execute('''
            SELECT store.{}, platform.{}, gamesplat.lang, gamesplat.link, 
            subscription.{}, subscription.d, subscription.m, subscription.y,
            gamesplat.isdemo FROM gamesplat
            INNER JOIN store ON store.id = gamesplat.storeid
            INNER JOIN platform ON platform.id = gamesplat.platformid
            LEFT JOIN subscription ON subscription.id = gamesplat.subscriptionid
            WHERE gamesplat.gameid = ?'''.format(view, view, view), (gameid,))
        storeplats = storeplats.fetchall()
        tags = self.cursor.execute('''
            SELECT tag.name FROM gametag
            INNER JOIN tag ON tag.id = gametag.tagid
            WHERE gametag.gameid = ?''', (gameid,))
        tags = tags.fetchall()
        tags = [x[0] for x in tags]
        gameinfos = self.cursor.execute('''
            SELECT game.id, game.title, game.year, franchise.name,
            game.vote, game.priority, game.img, game.note
            FROM game
            LEFT JOIN franchise ON franchise.id = game.franchiseid
            WHERE game.id = ?''', (gameid,))
        gameinfos = gameinfos.fetchall()
        return GameView(gameinfos[0], storeplats, tags)
    
    def _upd_group_dict(self, tdict, group, value):
        # This is a sub-function used by get_grouped_splat
        # It is used to update a single dict entry
        if group is None:
            group = ''
        if group not in tdict:
            tdict[group] = [ value ]
        else:
            tdict[group].append(value)
    
    def get_grouped_splat(self):
        ''' This function will return (grouped_stores, grouped_platforms)
        
        grouped_stores and grouped_platforms are dicts with:
        key: group_name
        value: list_of_items.
        
        Every item is a tuple representing a store or a platform (stores in
        grouped_stores; platforms in grouped_platforms). Inside tuple you will
        have:  id, name, icon
        '''
        gstores = {}
        gplatforms = {}
        for table, tdict in [('store', gstores), ('platform', gplatforms)]:
            entries = self.cursor.execute(
                '''SELECT splatgroup.name, {}.id, {}.name, {}.icon FROM {}
                LEFT JOIN splatgroup ON splatgroup.id = 
                {}.splatgroupid'''.format(*[table for x in range(5)])
            )
            entries = entries.fetchall()
            for entry in entries:
                self._upd_group_dict(tdict, entry[0], entry[1:])
        return (gstores, gplatforms)
    
    def commit(self):
        self.conn.commit()