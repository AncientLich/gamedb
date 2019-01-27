import os
import re
import sqlite3
import unittest
from gamedb.gamedb import GameDB
# from gamedb.gamedb import _FilterGamesJoinMMR
import gamedb
import datetime
import attr

'''
class TestFilterGamesJoinMMR(unittest.TestCase):
    def test_init_and_str(self):
        t = _FilterGamesJoinMMR('store', 'gamesplat', '=', None)
        self.assertEqual(str(t), '')
        with self.assertRaises(AttributeError):
            getattr(t, 'relation')
        # with self.assertRaises
        t = _FilterGamesJoinMMR('platform', 'gamesplat', '=', ['linux', 'PS4'])
        self.assertEqual(t.values, ['linux', 'ps4'])
        self.assertEqual(t.joins, [
            'INNER JOIN platform ON platform.id = gamesplat.platformid']
        )
        self.assertEqual(t.op, '=')
        self.assertEqual(t.where, 
            '(lower(platform.name) = ? OR lower(platform.name) = ?)'
        )
        self.assertEqual(str(t),
            '(SELECT gameid from gamesplat\n'
            'INNER JOIN platform ON platform.id = gamesplat.platformid\n'
            'WHERE (lower(platform.name) = ? OR lower(platform.name) = ?))'
        )
    
    def test_update(self):
        t1 = _FilterGamesJoinMMR('platform', 'gamesplat', '=', ['linux', 'PS4'])
        t2 = _FilterGamesJoinMMR('store', 'gamesplat', '=', ['psn', 'gog'])
        t3 = _FilterGamesJoinMMR('tag', 'gametag', '=', ['indie', 'adventure'])
        with self.assertRaises(ValueError):
            t1.update(15)
        with self.assertRaises(ValueError):
            t1.update(t3)
        t1.update(t2)
        self.assertEqual(t1.values, ['linux', 'ps4', 'psn', 'gog'])
        # this test will implicity ensure that _printJoins worlk correctly
        self.assertEqual(str(t1),
            '(SELECT gameid from gamesplat\n'
            'INNER JOIN platform ON platform.id = gamesplat.platformid\n'
            'INNER JOIN store ON store.id = gamesplat.storeid\n'
            'WHERE (lower(platform.name) = ? OR lower(platform.name) = ?) '
            'AND (lower(store.name) = ? OR lower(store.name) = ?))'
        )
'''


class TestGameDB(unittest.TestCase):
    def setUp(self):
        self.gamedb = GameDB(':memory:')
    
    def tearDown(self):
        self.gamedb.close()
    
    def test_create_tables(self):
        ts = self.gamedb.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")
        ts = ts.fetchall()
        tables = []
        for t in ts:
            t = dict(t)
            t = t['name']
            if 'sqlite' not in t:
                tables.append(t)
        self.assertEqual(tables, 
            ['splatgroup', 'store', 'platform', 'subscription', 'franchise', 
             'game', 'tag', 'gametag', 'gamesplat']
        )
    
    def test_mk_table_cmd(self):
        cmd = gamedb.cnv.mk_table_cmd(
            gamedb.items.Group,
            {gamedb.items.Store: gamedb.items.Store,
             gamedb.items.Platform: gamedb.items.Platform})
        self.assertEqual(cmd, 'CREATE TABLE IF NOT EXISTS splatgroup\n'
                              '(ID INTEGER PRIMARY KEY AUTOINCREMENT, '
                              'name TEXT)')
        cmd = gamedb.cnv.mk_table_cmd(
            gamedb.items.Game,
            {
                gamedb.items.Tag: gamedb.items.GameTag,
                gamedb.items.Store: gamedb.items.GameSplat,
                gamedb.items.Platform: gamedb.items.GameSplat
            })
        self.assertEqual(cmd, 'CREATE TABLE IF NOT EXISTS game\n'
                         '(ID INTEGER PRIMARY KEY AUTOINCREMENT, '
                         'name TEXT, year INTEGER, franchiseid INTEGER, '
                         'vote INTEGER, priority INTEGER, image TEXT, '
                         'note TEXT, '
                         'FOREIGN KEY(franchiseid) REFERENCES franchise(ID))')

        cmd = gamedb.cnv.mk_table_cmd(
            gamedb.items.GameSplat,
            (
               (gamedb.items.Game, gamedb.items.Store, gamedb.items.Platform), 
               {'subscriptionid': gamedb.items.Subscription}
            ))
        self.assertEqual(cmd, 'CREATE TABLE IF NOT EXISTS gamesplat\n'
            '(gameid INTEGER, storeid INTEGER, platformid INTEGER, '
            'lang TEXT, link TEXT, subscriptionid INTEGER, isdemo INTEGER, '
            'FOREIGN KEY(gameid) REFERENCES game(ID), '
            'FOREIGN KEY(storeid) REFERENCES store(ID), '
            'FOREIGN KEY(platformid) REFERENCES platform(ID), '
            'FOREIGN KEY(subscriptionid) REFERENCES subscription(ID), '
            'PRIMARY KEY(gameid, storeid, platformid))')
        cmd = gamedb.cnv.mk_table_cmd(gamedb.items.Subscription, {})
        self.assertEqual(cmd, 'CREATE TABLE IF NOT EXISTS subscription\n'
                               '(ID INTEGER PRIMARY KEY AUTOINCREMENT, '
                               'name TEXT, icon TEXT, '
                               'expire BLOB)')
    
    def test_x(self):
        pass