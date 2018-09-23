import os
import re
import sqlite3
import attr
import gamedb.itms
import gamedb.errors
import gamedb.rels
import gamedb.gameview
from datetime import date


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



def item_as_db_tuple(x):
    try:
        return x.toDB()
    except AttributeError:
        pass
    value = []
    for at in attr.fields(x.__class__):
        elem = getattr(x, at.name, None)
        if hasattr(elem, 'ID'):
            elem = getattr(elem, 'ID')
        elif isinstance(elem, bool):
            elem = int(elem)
        value.append(elem)
    return tuple(value)



'''
Class that manages all database operations for games.db
'''
class GameDB:
    def __init__(self, dbname):
        '''Intialize database (database_file)'''
        self.conn = sqlite3.connect(dbname)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._create_tables()
        self.cache = {}
        self.pending = {}
    
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
            image text, note text,
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
            name text UNIQUE NOT NULL, image text)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS splatgroup
            (id integer PRIMARY KEY AUTOINCREMENT, 
             name text UNIQUE NOT NULL)''')
        # if len(_list_tables) != N: <2>
        #     raise ValueError('database has more tables than expected')
    
    def _quick_item(self, cls, name):
        ''' add a new_item only by name
        
        quick_add will add default values to all fields 
        (usually an empty value). It will return a tuple:
        [0] -> id of the new item
        [1] -> dictionary with the details about the inserted item
        '''
        image = name.replace(' ', '_')
        image = image.lower() + '.png'
        params_table = {
            'store': {'ID': None, 'name': name, 'icon': image, 
                      'group': None},
            'platform': {'ID': None, 'name': name, 'icon': image, 
                         'group': None},
            'franchise': {'ID': None, 'name': name, 'image': image},
            'subscription': {'ID': None, 'name': name, 'icon': image, 
                            'expire': date(day=31, month=12, year=2010)},
            'tag': {'ID': None, 'name': name},
            'splatgroup': {'ID': None, 'name': name} }
        if cls.tablename not in params_table:
            raise ValueError('unvalid class for quick_add')
        params = params_table[cls.tablename]
        self.add(cls(**params))
        return self.item_from_name(cls, name)
    
    # calculate and return query, values for GameDB.filter_games
    def _fgquery(self, *, title=None, tags=None, platforms=None,
                     stores=None, franchise=None, page=1, 
                     sortby='title', limit=30, show_as_gameview=False):
        args = [title, tags, platforms, stores, franchise]
        # id, title, vote, priority, img
        query = (
            'SELECT * FROM game')
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
    
    def _fg(self, *, title=None, tags=None, platforms=None,
                     stores=None, franchise=None, page=1, sortby='title',
                     count_total=False, limit=30):
        # return tuple: (filtered list of games, total_games_found)
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
        result = [dict(self._patch_dict(x)) for x in result]
        if not count_total:
            return (result, None)
        query2 = re.sub(r'ORDER BY.*', '', query)
        query2 = 'SELECT count(*) FROM ({})'.format(query2)
        count = self.cursor.execute(query2, values)
        count = count.fetchall()
        count = dict(count[0])
        count = count['count(*)']
        return (result, count)
    
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
        
        The second value depends of count_total setting. If count_total is
        False the second value will be None. Otherwhise it is the number of
        total games found with that filter
        
        Notes:
        (*) Must be a list even if only one item must be checked. So you need
        to use a list of one element only if you need to search only one item.
        '''
        result = []
        gamelist, count = self._fg(title=title, tags=tags, platforms=platforms,
                                   stores=stores, franchise=franchise, 
                                   page=page, sortby=sortby,
                                   count_total=count_total, limit=limit)
        result = [gamedb.itms.Game(**game) for game in gamelist]
        return (result, count)
    
    def item_from_id(self, cls, value):
        ''' find an item from id value
        
        params:
        cls -> item class type (example: Store)
        value -> item id in that table (example: a Store item stored 
                 in store table)
        '''
        if value is None:
            return None
        xdict = self.cursor.execute(
            'SELECT * FROM {} WHERE id=?'.format(cls.tablename),
            (value,))
        xdict = xdict.fetchall()
        xdict = dict(xdict[0])
        xdict = self._patch_dict(xdict)
        return self._get_cached_item(cls(**xdict))
    
    def item_from_name(self, cls, name, *, create_if_new=False):
        ''' find the item with the desired name (name must be complete)
        
        params:
        cls -> item class type (example: Store)
        name -> item name in that table (case insensitive)
        '''
        if name is None:
            return None
        label = '{}.{}'.format(cls.tablename, name.lower())
        if label in self.cache:
            return self.cache[label]
        colname = 'name' if cls.tablename != 'game' else 'title'
        value = self.cursor.execute(
            'SELECT * from {} WHERE lower({})=?'.format(cls.tablename, colname), 
            (name.lower(),))
        value = value.fetchall()
        if len(value) == 0:
            if not create_if_new:
                raise gamedb.errors.ItemNotFoundError(cls.tablename, name)
            item = self._quick_item(cls, name)
            self.pending[label] = item
            return item
        value = dict(value[0])
        value = self._patch_dict(value)
        self.cache[label] = cls(**value)
        return self.cache[label]
    
    def get_matching_item(self, item):
        # 1) if item is stored in cache, return cached item
        name = getattr(item, 'name', None)
        if name is None:
            name = getattr(item, 'title', 'NULL')
        label = '{}.{}'.format(item.tablename, name.lower())
        if label in self.cache:
            return self.cache[label]
        # 2) if item is a GameView or Place return error
        elif isinstance(item, 
                      (gamedb.gameview.GameView, 
                       gamedb.gameview.Place)):
            raise ValueError('get_matching_item cannot be used with '
                'GameView or Place item')
        # 3) if item is GameTag or GameSplat search it from database looking
        #    for their primary key values
        elif isinstance(item, gamedb.rels.GameTag):
            result = self.cursor.execute(
                'SELECT * FROM gametag WHERE gameid = ? AND '
                'tagid = ?', (item.gameid, item.tagid))
        elif isinstance(item, gamedb.rels.GameSplat):
            result = self.cursor.execute(
                'SELECT * FROM gamesplat WHERE gameid = ? AND '
                'storeid = ? AND platformid = ?', 
                (item.gameid, item.storeid, item.platformid))
        # 4) in all other cases ('standard' item with ID property currently
        #    not stored in cache) search it by item ID and store it in memory,
        #    if found
        elif item.ID is None:
            xname = getattr(item, 'name', None)
            if xname is None:
                xname = getattr(item, 'title')            
            try:
                return self.item_from_name(type(item), xname)
            except gamedb.errors.ItemNotFoundError:
                return None
        else:
            return self.item_from_id(type(item), item.ID)
        # --------------
        # 3) (Part II) - calculate resulted item for case 3 and return it
        # If table is GameTag or GameSplat, then the following lines will 
        # return the new item
        cls = type(item)
        result = result.fetchall()
        if len(result) == 0:
            return None
        result = dict(result[0])
        return cls(result)
    
    def add(self, item, *, duplicate_raises_error=True):
        if isinstance(item, (tuple, list)):
            for i in item:
                self.add(i, duplicate_raises_error=duplicate_raises_error)
            return
        elif isinstance(item, gamedb.gameview.GameView):
            self.add(
                gamedb.itms.Game(item.ID, item.title, item.year, 
                                    item.franchise, item.vote, 
                                    item.priority, item.image, item.note),
                duplicate_raises_error=False)
            new_item = self.item_from_name(
                    gamedb.itms.Game, item.title)
            xid = new_item.ID
            for tag in item.tags:
                self.add(gamedb.rels.GameTag(xid, tag.ID))
            for place in item.places:
                self.add(place.toGameSplat(gameid=xid))
            return
        insertion_tup = item_as_db_tuple(item)
        insert = 'INSERT'
        if isinstance(item, gamedb.rels.GameTag):
            insert = 'INSERT OR IGNORE'
        elif isinstance(item, gamedb.rels.GameSplat):
            insert = 'INSERT OR IGNORE'
            if not item.isdemo:
                existing_gamesplat = self.get_matching_item(item)
                wasdemo = getattr(existing_gamesplat, 'isdemo', False)
                if wasdemo:
                    insert = 'UPDATE'
        else:
            tmp = self.get_matching_item(item)
            if tmp is not None:
                if duplicate_raises_error:
                    raise gamedb.errors.ItemExistsError(item)
                else:
                    return
        self.cursor.execute(
            '{} INTO {} VALUES ({})'.format(
                insert, item.tablename,
                ','.join('?' for x in insertion_tup)),
            insertion_tup)
    
    def _patch_dict(self, xdict):
        xdict = dict(xdict)
        try:
            xdict['ID'] = xdict.pop('id')
        except KeyError:
            pass
        for old, new, cls2 in [('splatgroupid', 'group', gamedb.itms.Group),
                               ('franchiseid', 'franchise', 
                                gamedb.itms.Franchise)]:
            if old in xdict:
                xdict[new] = self.item_from_id(cls2, xdict.pop(old))
        if 'd' in xdict:
            d = xdict.pop('d')
            m = xdict.pop('m')
            y = xdict.pop('y')
            xdict['expire'] = date(day=d, month=m, year=y)
        return xdict
    
    def _get_cached_item(self, item):
        if item.tablename is None or item.tablename in {'game', 'gametag', 
                                                        'gamesplat'}:
            return item
        label = '{}.{}'.format(item.tablename, item.name.lower())
        if label not in self.cache:
            self.cache[label] = item
        return self.cache[label]
    
    def gameview(self, game):
        if isinstance(game, int):
            game = self.item_from_id(gamedb.itms.Game, game)
        elif not isinstance(game, gamedb.itms.Game):
            raise ValueError('gameview requires int or Game parameter')
        gamesplats = self.cursor.execute(
            'SELECT * FROM gamesplat WHERE gamesplat.gameid = ?', (game.ID,))
        gamesplats = gamesplats.fetchall()
        gamesplats = [dict(x) for x in gamesplats]
        places = []
        for gamesplat in gamesplats:
            store = self.item_from_id(gamedb.itms.Store, gamesplat['storeid'])
            platform = self.item_from_id(
                gamedb.itms.Platform, gamesplat['platformid'])
            subscription = self.item_from_id(
                gamedb.itms.Subscription, gamesplat['subscriptionid'])
            places.append(
                gamedb.gameview.Place(
                    store, platform, gamesplat['lang'], gamesplat['link'],
                    subscription, gamesplat['isdemo']))
        tags = self.cursor.execute(
            'SELECT tag.id, tag.name FROM gametag '
            'INNER JOIN tag ON tag.id = gametag.tagid '
            'WHERE gametag.gameid = ?', (game.ID,))
        tags = tags.fetchall()
        tags = [self._get_cached_item(
                    gamedb.itms.Tag(** self._patch_dict(dict(t)))) 
                for t in tags]
        gameview = attr.asdict(game)
        gameview['tags'] = tags
        gameview['places'] = places
        return gamedb.gameview.GameView(**gameview)
    
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
        
        tmp = {}
        
        for cls in (gamedb.itms.Group, gamedb.itms.Store, gamedb.itms.Platform):
            items = self.cursor.execute(
                'SELECT * FROM {}'.format(cls.tablename))
            items = items.fetchall()
            items = [self._get_cached_item(cls(** self._patch_dict(dict(item)))) 
                     for item in items]
            tmp[cls.tablename] = items
        
        gstores = self._ggs2(tmp['store'])
        gplatforms = self._ggs2(tmp['platform'])
        return (gstores, gplatforms)
    
    def _ggs2(self, items):
        # this function 'completes' get_grouped_splat
        result = {'': []}
        for item in items:
            if item.group is None:
                result[''].append(item)
            else:
                if item.group.name not in result:
                    result[item.group.name] = []
                result[item.group.name].append(item)
        return result
    
    def commit(self):
        self.conn.commit()