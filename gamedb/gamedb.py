import os
import re
import sqlite3


class GameDB:
    def __init__(self, dbname):
        self.conn = sqlite3.connect(dbname)
        self.cursor = self.conn.cursor()
        self._create_tables()
        self.filters = {}
        self.fields = ('id', 'name', 'icon', 'device', 'title', 'year',
                       'franchiseid', 'vote', 'priority', 'img', 'note',
                       'link', 'd', 'm', 'y',
                       'gameid', 'tagid', 'storeid', 'platformid',
                       'subscriptionid')
    
    def _create_tables(self):
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
    
    def _list_tables(self):
        tmp = self.cursor.execute("""
            SELECT name FROM sqlite_master WHERE type='table'""")
        tmp = tmp.fetchall()
        tables = [table[0] for table in tmp] 
        return [table for table in tables if 'sqlite' not in table]
    
    def _addgame_item(self, title, year=2000, franchise=None, vote=None, 
                 priority=6, img=None, note=None):
        self.cursor.execute(
            "INSERT INTO game VALUES (NULL, ?,?,?, ?,?,?, ?)",
            (title, year, franchise, vote, priority, img, note)
        )
        self.conn.commit()
    
    # trigger = gog, steam, uplay, humblebundle etc triggers 'pc' platform
    def add_platform(self, name, device, icon=None):
        self.cursor.execute(
            "INSERT INTO platform VALUES (NULL, ?,?,?)",
            (name, device, icon)
        )
        self.conn.commit()
    
    def add_store(self, name, icon=None):
        self.cursor.execute(
            "INSERT INTO store VALUES (NULL, ?,?)",
            (name, icon)
        )
        self.conn.commit()
    
    def add_tag(self, name):
        self.cursor.execute(
            "INSERT INTO tag VALUES (NULL,?)", (name,)
        )
        self.conn.commit()
    
    def add_franchise(self, name, img=None):
        self.cursor.execute(
            "INSERT INTO franchise VALUES (NULL,?,?)", (name,img)
        )
        self.conn.commit()
    
    def add_subscription(self, name, icon, d, m, y):
        self.cursor.execute(
            "INSERT INTO subscription VALUES (NULL,?,?, ?,?,?)", 
            (name, icon,  d, m, y)
        )
        self.conn.commit()
    
    def _addgamesplat(self, gameid, storeid, platformid, link=None, 
                      subscriptionid=None):
        self.cursor.execute(
            'INSERT OR IGNORE INTO gamesplat VALUES(?,?,?, ?,?)',
            (gameid, storeid, platformid, link, subscriptionid)
        )
    
    def _addgametag(self, gameid, tagid):
        self.cursor.execute(
            'INSERT OR IGNORE INTO gametag VALUES(?,?)',
            (gameid, tagid)
        )
    
    def _sid(self, table, param, value):
        if value is not None:
            myval = self.cursor.execute(
                "SELECT id FROM {} WHERE lower({})=?".format(table, param), 
                (value.lower(),)
            )
            myval = myval.fetchall()
            if len(myval) == 0:
                return None
            else:
                return myval[0][0]
        else:
            return None
    
    def add_game(self, subscription, priority, title, tag, franchise,
                    year, vote, img, lang, store, platform, link, note):
        franchiseid = self._sid('franchise', 'name', franchise)
        platid = self._sid('platform', 'name', platform)
        storeid = self._sid('store', 'name', store)
        tagid = self._sid('tag', 'name', tag)
        subsid = self._sid('subscription', 'name', subscription)
        for xid, tab, xname in [(platid, 'platform', platform), 
                                (storeid, 'store', store),
                                (tagid, 'tag', tag),
                                (franchiseid, 'franchise', franchise),
                                (subsid, 'subscription', subscription)]:
            if xid is None and xname is not None:
                raise ValueError('{} "{}" not found in database'.format(
                    tab, xname)
                )
            if tab in ('platform', 'store') and xname is None:
                raise ValueError('{} {}.\n{}="{}"'.format(
                    'Unexpected None value for', tab,
                    'Matched on title', title)
                )
        gid = self._sid('game', 'title', title)
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
    
    def _validate_filters(self, table, field, value, fop=None):
        if fop is not None and fop not in ('==',):
            raise ValueError('invalid operator for "fop": {}', fop)
        elif table not in self._list_tables():
            raise ValueError('invalid table: {}', table)
        elif field not in self.fields:
            raise ValueError('invalid field: {}', field)
    
    def _mk_filterkey(self, table, field, value):
        if table == 'store' or table == 'platform':
            return '{}=={}'.format(table, value)
        else:
            return '{}.{}'.format(table, field)
    
    def new_filter(self, table, field, fop, value):
        self._validate_filters(table, field, value, fop)
        key = self._mk_filterkey(table, field, value)
        self.filters[key] = ('{}.{} {} '.format(table, field, fop), value)
    
    def del_filter(self, table, field, value):
        self._validate_filters(table, field, value)
        key = self._mk_filterkey(table, field, value)
        self.filters.pop(key, None)
    
    def close(self):
        self.conn.close()
    

