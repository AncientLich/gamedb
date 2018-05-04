import os
import re
import sqlite3
import unittest
from gamedb.gamedb import *



class TestGameDB(unittest.TestCase):
    def setUp(self):
        self.gamedb = GameDB('test.db')
    
    def tearDown(self):
        self.gamedb.close()
        os.remove('test.db')
    
    def test_create_tables(self):
        tables = self.gamedb._list_tables()
        self.assertEqual(tables, 
            ['subscription', 'game', 'platform', 'store', 'gamesplat', 
             'tag', 'gametag','franchise']
        )
        
    def test_addgame_base(self):
        self.gamedb._addgame_item('Bloodborne')
        val = self.gamedb.searchgame('Bloodborne')
        self.assertEqual(val[0][0], 1)
        self.assertEqual(val[0][1], 'Bloodborne')
        self.assertEqual(len(val), 1)
        # testing sid
        val = self.gamedb._sid('game','title', 'Bloodborne')
        self.assertEqual(val, 1)
        val = self.gamedb._sid('game','title', 'Nobun')
        self.assertIs(val, None)
        
    def test_add_platform(self):
        for b, l in [('ps', ('ps3', 'ps4', 'psvita')), 
                     ('pc', ('win', 'linux', 'mac'))]:
            for a in l:
                self.gamedb.add_platform(a,b)
        value = self.gamedb.cursor.execute(
            'SELECT id, name, device FROM platform'
        )
        value = value.fetchall()
        self.assertEqual(value, 
            [(1, 'ps3', 'ps'), (2, 'ps4', 'ps'), 
             (3, 'psvita', 'ps'), (4, 'win', 'pc'), 
             (5, 'linux', 'pc'), (6, 'mac', 'pc')]
        )
    
    def test_add_store(self):
        for i in ['psn', 'steam', 'gog', 'uplay', 'cd', 'hd']:
            self.gamedb.add_store(i)
        value = self.gamedb.cursor.execute('SELECT id, name from store')
        value = value.fetchall()
        self.assertEqual(value,
            [(1, 'psn'), (2, 'steam'), (3, 'gog'), (4, 'uplay'),
             (5, 'cd'), (6, 'hd')]
        )
    
    def test_add_game_csv(self):
        first = True
        self.gamedb.add_platform('ps4', 'ps')
        self.gamedb.add_platform('linux', 'pc')
        self.gamedb.add_store('psn')
        self.gamedb.add_store('steam')
        self.gamedb.add_tag('action')
        self.gamedb.add_tag('indie')
        self.gamedb.add_tag('adventure')
        self.gamedb.add_franchise("Don’t Starve")
        self.gamedb.add_subscription('ps+', 'psplus.png', 11, 4, 2018)
        with open('test_games.csv', 'r', encoding='utf-8') as fi:
            for xline in fi:
                if not first:
                    params = xline.split(',')
                    for i, param in enumerate(params):
                        if i == 1 or i == 5 or i == 6:
                            if param is not None:
                                params[i] = int(param)
                        else:
                            params[i] = param.strip()
                            if param == '':
                                params[i] = None
                    self.gamedb.add_game(*params)
                else:
                    first = False
        # ------ GAMEPSLAT -------
        gid1 = self.gamedb._sid('game', 'title', 'Bloodborne')
        gid2 = self.gamedb._sid('game', 'title', "Don’t Starve")
        pid1 = self.gamedb._sid('platform', 'name', 'ps4')
        pid2 = self.gamedb._sid('platform', 'name', 'linux')
        sid1 = self.gamedb._sid('store', 'name', 'psn')
        sid2 = self.gamedb._sid('store', 'name', 'steam')
        res = self.gamedb.cursor.execute(
            'SELECT gameid, storeid, platformid from gamesplat')
        res = res.fetchall()
        self.assertEqual( sorted(res), sorted(
            [(gid1, sid1, pid1),(gid2, sid2, pid2)]) )
        # ---- GAMETAG ---------
        tag1a = self.gamedb._sid('tag', 'name', 'action')
        tag1b = self.gamedb._sid('tag', 'name', 'adventure')
        tag2 = self.gamedb._sid('tag', 'name', 'indie')
        res = self.gamedb.cursor.execute(
            'SELECT gameid, tagid from gametag'
        )
        res = res.fetchall()
        self.assertEqual(sorted(res), sorted(
            [(gid1, tag1a), (gid1, tag1b), (gid2, tag2)]) )
        # ------ FRANCHISE -------------------
        f = self.gamedb._sid('franchise', 'name', "Don’t Starve")
        res = self.gamedb.cursor.execute(
            'SELECT title, franchiseid from game'
        )
        res = res.fetchall()
        for game, frid in res:
            if game == "Don’t Starve":
                self.assertEqual(frid, self.gamedb._sid('franchise', 'name',
                                                        "Don’t Starve"))
            else:
                self.assertIs(frid, None)
    
    def test_add_gamesplat(self):
        self.gamedb.add_platform('ps4', 'ps')
        self.gamedb.add_platform('win', 'pc')
        self.gamedb.add_store('psn')
        self.gamedb.add_store('steam')
        self.gamedb._addgame_item('Bloodborne')
        self.gamedb._addgamesplat(1,1,1)
        with self.assertRaises(sqlite3.IntegrityError):
            self.gamedb._addgamesplat(5,5,5)
    
    def test_add_tag(self):
        for i in ('platform', 'indie', 'point-click'):
            self.gamedb.add_tag(i)
        for n,v in [(1, 'platform'), (2, 'indie'), (3, 'point-click')]:
            val = self.gamedb._sid('tag', 'name', v)
            self.assertEqual(val, n)
    
    def test_add_franchise(self):
        for i in ("Don't Starve", 'Bloodborne'):
            self.gamedb.add_franchise(i)
        for n,v in [(1, "Don't Starve"), (2, 'Bloodborne')]:
            val = self.gamedb._sid('franchise', 'name', v)
            self.assertEqual(val, n)
    
    def test_add_gametag(self):
        self.gamedb.add_tag('horror')
        self.gamedb._addgame_item('Bloodborne')
        self.gamedb._addgametag(1,1)
        with self.assertRaises(sqlite3.IntegrityError):
            self.gamedb._addgametag(5,5)
    
    def test_add_subscription(self):
        self.gamedb.add_subscription('ps+', 'psplus.png', 11,4,2018)
        res = self.gamedb.cursor.execute(
            'SELECT * from subscription'
        )
        res = res.fetchall()
        self.assertEqual(res, [(1, 'ps+', 'psplus.png', 11,4,2018)])
    
    def test_validate_filters(self):
        for field in self.gamedb.fields:
            with self.assertRaises(ValueError):
                self.gamedb._validate_filters(field, field, None)
        for table in self.gamedb._list_tables():
            with self.assertRaises(ValueError):
                self.gamedb._validate_filters(table, table, None)
                
    def test_mk_filterkey(self):
        for table, values in [('platform', ['ps4', 'ps_vita', 'ps3',
                                            'win', 'linux', 'mac']),
                              ('store', ['steam', 'gog', 'uplay', 'psn'])]:
            for value in values:
                self.assertEqual(
                    self.gamedb._mk_filterkey(table, 'name', value),
                    '{}=={}'.format(table, value)
                )
        for table, field, value in [('game', 'name', 'Bloodborne'),
                                    ('tag', 'id', 3),
                                    ('franchise', 'img', 'txt.txt'),
                                    ('subscription', 'd', 22)]:
            self.assertEqual(
                self.gamedb._mk_filterkey(table, field, value),
                '{}.{}'.format(table, field)
            )
    
    def test_newdel_filter(self):
        # this will test both new_filter and del_filter
        self.gamedb.new_filter('game', 'name', '==', 'Bloodborne')
        self.gamedb.new_filter('store', 'name', '==', 'psn')
        self.gamedb.new_filter('platform', 'name', '==', 'linux')
        self.assertEqual(
            sorted(self.gamedb.filters),
            sorted(
                {'store==psn': ('store.name == ', 'psn'),
                 'platform==linux': ('platform.name == ', 'linux'),
                  'game.name': ('game.name == ', 'Bloodborne')}
            )
        )
        self.gamedb.del_filter('store', 'name', 'psn')
        self.gamedb.del_filter('game', 'name', 'Bloodborne')
        # this last filter does not exist, so this command will be 'ignored'
        # filters will be not modified after the following command:
        self.gamedb.del_filter('platform', 'name', 'mac')
        # now checking if all is good
        self.assertEqual(
            self.gamedb.filters,
            {'platform==linux': ('platform.name == ', 'linux')}
        )
    
    def test_pass(self):
        pass