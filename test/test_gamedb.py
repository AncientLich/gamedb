import os
import re
import sqlite3
import unittest
from gamedb.gamedb import GameDB
from gamedb.gamedb import _FilterGamesJoinMMR
from gamedb.gameview import GameView
import gamedb
import datetime
import attr


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
            ['subscription', 'game', 'platform', 'store', 'gamesplat', 
             'tag', 'gametag', 'franchise', 'splatgroup']
        )
    
    def add_misc_01(self):
        self.gamedb.add(gamedb.Tag(
            name='Action', ID=None))
        self.gamedb.add(gamedb.Group(
            name='PC', ID=None))
        self.gamedb.add(gamedb.Franchise(
            name="Don't Starve", image='ds.png', ID=None))
        self.gamedb.add(gamedb.Subscription(
            name="PS+", icon="psplus.png", ID=None, 
            expire=datetime.date(day=30, month=12, year=2100)))
        self.gamedb.add(gamedb.Store(
            name="steam", icon="steam.png", ID=None, 
            group=None))
        self.gamedb.add(gamedb.Platform(
            name='linux', icon='linux.png', ID=None, 
            group=self.gamedb.item_from_name(gamedb.Group, 'PC')))
        self.gamedb.add(gamedb.GameView(
            ID=None, title='Bloodborne', year=2010, 
            franchise=None, vote=90, priority=9,
            image='bb.png', note=None,
            tags=[self.gamedb.item_from_name(gamedb.Tag, 'action')],
            places=[
                gamedb.Place(
                      store=self.gamedb.item_from_name(
                          gamedb.Store, 'steam'),
                      platform=self.gamedb.item_from_name(
                          gamedb.Platform, 'linux'),
                      lang="ita",
                      link="my_link",
                      subscription=self.gamedb.item_from_id(
                          gamedb.Subscription, 1))
            ]))
        self.gamedb.add(gamedb.Game(
            ID=None, title="Don't Starve", year=2010, 
            franchise=self.gamedb.item_from_id(gamedb.Franchise, 1), 
            vote=90, priority=9,
            image='ds.png', note=None))
        self.gamedb.add(gamedb.Game(
            ID=None, title='Hollow Knight', year=2010, 
            franchise=None, vote=90, priority=9,
            image='hk.png', note=None))
    
    def add_misc_02(self):
        self.gamedb.add(gamedb.Store(
            name="gog", icon="gog.png", ID=None, 
            group=None))
        self.gamedb.add(gamedb.Platform(
            name='win', icon='win.png', ID=None, 
            group=self.gamedb.item_from_name(gamedb.Group, 'PC')))
        self.gamedb.add(gamedb.Tag(ID=None, name='indie'))
        self.gamedb.add(gamedb.GameView(
            ID=None, title="Assassin's Creed", year=2010, 
            franchise=None, vote=90, priority=9,
            image='ac.png', note=None,
            tags=[self.gamedb.item_from_name(gamedb.Tag, 'action')],
            places=[
                gamedb.Place(
                      store=self.gamedb.item_from_name(
                          gamedb.Store, 'gog'),
                      platform=self.gamedb.item_from_name(
                          gamedb.Platform, 'win'),
                      lang="ita",
                      link="my_link",
                      subscription=None)
            ]))
        self.gamedb.add(gamedb.GameView(
            ID=None, title='Dust', year=2010, 
            franchise=None, vote=90, priority=9,
            image='dust.png', note=None,
            tags=[self.gamedb.item_from_id(gamedb.Tag, 1),
                  self.gamedb.item_from_id(gamedb.Tag, 2)],
            places=[
                gamedb.Place(
                      store=self.gamedb.item_from_name(
                          gamedb.Store, 'gog'),
                      platform=self.gamedb.item_from_name(
                          gamedb.Platform, 'win'),
                      lang="ita",
                      link="my_link_1",
                      subscription=None),
                gamedb.Place(
                      store=self.gamedb.item_from_name(
                          gamedb.Store, 'gog'),
                      platform=self.gamedb.item_from_name(
                          gamedb.Platform, 'linux'),
                      lang="ita",
                      link="my_link_2",
                      subscription=None),
                gamedb.Place(
                      store=self.gamedb.item_from_name(
                          gamedb.Store, 'steam'),
                      platform=self.gamedb.item_from_name(
                          gamedb.Platform, 'win'),
                      lang="ita",
                      link="my_link_3",
                      subscription=None),
                gamedb.Place(
                      store=self.gamedb.item_from_name(
                          gamedb.Store, 'steam'),
                      platform=self.gamedb.item_from_name(
                          gamedb.Platform, 'linux'),
                      lang="ita",
                      link="my_link_4",
                      subscription=None)
            ]))
        self.gamedb.add(gamedb.GameView(
                ID=None, title="Don't Starve Together", year=2010, 
                franchise=self.gamedb.item_from_id(gamedb.Franchise, 1), 
                vote=90, priority=9, image='ds.png', note=None,
                tags=[self.gamedb.item_from_id(gamedb.Tag, 1)],
                places=[
                    gamedb.Place(
                      store=self.gamedb.item_from_name(
                          gamedb.Store, 'steam'),
                      platform=self.gamedb.item_from_name(
                          gamedb.Platform, 'linux'),
                      lang="ita",
                      link="my_link_4",
                      subscription=None)
                ]))
        # ...
    
    def test_add_00(self):
        '''first test for GameDB.add
        
        this will simply test if adding Game(s) works'''
        self.gamedb.add(gamedb.Game(
            ID=None, title='Bloodborne', year=2010, 
            franchise=None, vote=90, priority=9,
            image='bb.png', note=None))
        self.gamedb.add(gamedb.Game(
            ID=None, title="Don't Starve", year=2010, 
            franchise=None, vote=90, priority=9,
            image='ds.png', note=None))
        self.gamedb.add(gamedb.Game(
            ID=None, title='Hollow Knight', year=2010, 
            franchise=None, vote=90, priority=9,
            image='hk.png', note=None))
        results = self.gamedb.cursor.execute('SELECT * FROM game')
        results = results.fetchall()
        results = [gamedb.Game(** dict(self.gamedb._patch_dict(x)))
                   for x in results]
        self.assertEqual(
            sorted(results),
            [gamedb.Game(ID=1, title='Bloodborne', year=2010, 
                                 franchise=None, vote=90, priority=9,
                                 image='bb.png', note=None),
             gamedb.Game(ID=2, title="Don't Starve", year=2010, 
                                 franchise=None, vote=90, priority=9,
                                 image='ds.png', note=None),
             gamedb.Game(ID=3, title='Hollow Knight', year=2010, 
                                 franchise=None, vote=90, priority=9,
                                 image='hk.png', note=None)])
        
    def test_add_01(self):
        '''another test for GameDB.add
        
        this will do a step further. It will try to add objects with
        nested objects and check if cache is correctly used, checking
        object identities when necessary.'''
        self.add_misc_01()
        self.gamedb.commit()
        tag1a = self.gamedb.item_from_id(gamedb.Tag, 1)
        tag1b = self.gamedb.item_from_id(gamedb.Tag, 1)
        self.assertEqual(tag1a, gamedb.Tag(name='Action', ID=1))
        self.assertIs(tag1a, tag1b)
        grp1a = self.gamedb.item_from_id(gamedb.Group, 1)
        grp1b = self.gamedb.item_from_id(gamedb.Group, 1)
        self.assertEqual(grp1a, gamedb.Group(name='PC', ID=1))
        self.assertIs(grp1a, grp1b)
        str1a = self.gamedb.item_from_id(gamedb.Store, 1)
        str1b = self.gamedb.item_from_id(gamedb.Store, 1)
        self.assertEqual(str1a, 
            gamedb.Store(name='steam', icon='steam.png', ID=1, group=None))
        self.assertIs(str1a, str1b)
        plt1a = self.gamedb.item_from_id(gamedb.Platform, 1)
        plt1b = self.gamedb.item_from_id(gamedb.Platform, 1)
        self.assertEqual(plt1a, 
            gamedb.Platform(name='linux', icon='linux.png', ID=1, group=grp1a))
        self.assertIs(plt1a, plt1b)
        fch1a = self.gamedb.item_from_id(gamedb.Franchise, 1)
        fch1b = self.gamedb.item_from_id(gamedb.Franchise, 1)
        self.assertEqual(fch1a, 
            gamedb.Franchise(name="Don't Starve", image='ds.png', ID=1))
        self.assertIs(fch1a, fch1b)
        sub1a = self.gamedb.item_from_id(gamedb.Subscription, 1)
        sub1b = self.gamedb.item_from_id(gamedb.Subscription, 1)
        self.assertEqual(sub1a, 
            gamedb.Subscription(
                name="PS+", icon='psplus.png', ID=1,
                expire=datetime.date(day=30, month=12, year=2100)))
        self.assertIs(sub1a, sub1b)
        # checking gametags...
        result = self.gamedb.cursor.execute('SELECT * FROM gametag')
        result = result.fetchall()
        self.assertEqual(len(result), 1)
        result = self.gamedb._patch_dict(dict(result[0]))
        result = gamedb.GameTag(**result)
        self.assertEqual(result, gamedb.GameTag(1, 1))
        # checking gamesplats....
        result = self.gamedb.cursor.execute('SELECT * FROM gamesplat')
        result = result.fetchall()
        self.assertEqual(len(result), 1)
        result = self.gamedb._patch_dict(dict(result[0]))
        result = gamedb.GameSplat(**result)
        self.assertEqual(
            result, gamedb.GameSplat(1, 1, 1, "ita", "my_link", 1, False))
        # checking 'is' inside objects
        self.assertIs(plt1a.group, plt1b.group)
        self.assertIs(plt1a.group, grp1a)
        game = self.gamedb.item_from_id(gamedb.Game, 2)
        self.assertIs(game.franchise, fch1a)
    
    def test_add_02(self):
        '''testing again GameDB.add
        
        The series of tests for GameDB.add is continuing.
        Now testing 'errors' while trying to insert objects'''
        with self.assertRaises(gamedb.ItemNotFoundError):
            self.gamedb.item_from_name(gamedb.Store, 'PS Store')
        with self.assertRaises(gamedb.ItemNotFoundError):
            self.gamedb.item_from_name(gamedb.Group, 'PC')
        item = self.gamedb.item_from_name(gamedb.Store, 'gog', 
                                          create_if_new=True)
        self.assertEqual(
            item, gamedb.Store(name='gog', ID=1, icon='gog.png', group=None))
        with self.assertRaises(gamedb.ItemExistsError):
            self.gamedb.add(item, duplicate_raises_error=True)
        self.gamedb.add(item, duplicate_raises_error=False)
        self.assertIs(item, self.gamedb.item_from_id(gamedb.Store, 1))
    
    def test_filter_games(self):
        self.add_misc_01()
        self.add_misc_02()
        self.gamedb.commit()
        games, _ = self.gamedb.filter_games(tags=['indie'])
        self.assertEqual(
            games,
            [self.gamedb.item_from_name(gamedb.itms.Game, 'dust')])
        games, _ = self.gamedb.filter_games(tags=['action'])
        self.assertEqual(
            games,
            [self.gamedb.item_from_name(gamedb.Game, "Assassin's Creed"),
             self.gamedb.item_from_name(gamedb.Game, 'Bloodborne'),
             self.gamedb.item_from_name(gamedb.Game, "Don't Starve Together"),             
             self.gamedb.item_from_name(gamedb.Game, 'Dust')])
        games, _ = self.gamedb.filter_games(tags=['action', 'indie'])
        self.assertEqual(
            games,
            [self.gamedb.item_from_name(gamedb.Game, "Assassin's Creed"),
             self.gamedb.item_from_name(gamedb.Game, 'Bloodborne'),
             self.gamedb.item_from_name(gamedb.Game, "Don't Starve Together"),             
             self.gamedb.item_from_name(gamedb.Game, 'Dust')])
        games, _ = self.gamedb.filter_games(franchise="Starve", tags=['action'])
        self.assertEqual(
            games,
            [self.gamedb.item_from_name(gamedb.Game, "Don't Starve Together")])
    
    def test_gameview(self):
        self.add_misc_01()
        self.add_misc_02()
        self.gamedb.commit()
        places=[
            gamedb.Place(
                store=self.gamedb.item_from_name(gamedb.Store, 'gog'),
                platform=self.gamedb.item_from_name(gamedb.Platform, 'win'),
                lang="ita", link="my_link_1", subscription=None),
            gamedb.Place(
                store=self.gamedb.item_from_name(gamedb.Store, 'gog'),
                platform=self.gamedb.item_from_name(gamedb.Platform, 'linux'),
                lang="ita", link="my_link_2", subscription=None),
            gamedb.Place(
                store=self.gamedb.item_from_name(gamedb.Store, 'steam'),
                platform=self.gamedb.item_from_name(gamedb.Platform, 'win'),
                lang="ita", link="my_link_3", subscription=None),
            gamedb.Place(
                store=self.gamedb.item_from_name(gamedb.Store, 'steam'),
                platform=self.gamedb.item_from_name(gamedb.Platform, 'linux'),
                lang="ita", link="my_link_4", subscription=None)]
        gv = attr.asdict(self.gamedb.item_from_name(gamedb.Game, 'Dust'))
        gv['places'] = places
        gv['tags'] = [self.gamedb.item_from_id(gamedb.Tag, 1),
                      self.gamedb.item_from_id(gamedb.Tag, 2)]
        gv = gamedb.GameView(**gv)
        gv2 = self.gamedb.gameview(gv.ID)
        gv.places = sorted(gv.places)
        gv2.places = sorted(gv2.places)
        self.assertEqual(gv, gv2)
    
    def test_group_splat(self):
        self.gamedb.add(gamedb.Group(ID=None, name='Physical'))
        self.gamedb.add(gamedb.Group(ID=None, name='PC'))
        self.gamedb.add(gamedb.Store(ID=None, name='steam', icon='steam.png', 
            group=None))
        self.gamedb.add(gamedb.Store(ID=None, name='gog', icon='gog.png', 
            group=None))
        self.gamedb.add(gamedb.Store(ID=None, name='cd', icon='cd.png',
            group=self.gamedb.item_from_name(gamedb.Group, 'physical')))
        self.gamedb.add(gamedb.Store(ID=None, name='hd', icon='hd.png',
            group=self.gamedb.item_from_name(gamedb.Group, 'physical')))
        self.gamedb.add(gamedb.Platform(ID=None, name='android', 
            icon='android.png', group=None))
        self.gamedb.add(gamedb.Platform(ID=None, name='win', icon='win.png',
            group=self.gamedb.item_from_name(gamedb.Group, 'pc')))
        self.gamedb.add(gamedb.Platform(ID=None, name='linux', 
            icon='linux.png', 
            group=self.gamedb.item_from_name(gamedb.Group, 'pc')))
        self.gamedb.add(gamedb.Platform(ID=None, name='mac', icon='mac.png',
            group=self.gamedb.item_from_name(gamedb.Group, 'pc')))
        gstores, gplatforms = self.gamedb.get_grouped_splat()
        self.assertEqual(
            gstores,
            {'': [self.gamedb.item_from_name(gamedb.Store, 'steam'), 
                  self.gamedb.item_from_name(gamedb.Store, 'gog')], 
             'Physical': 
                 [self.gamedb.item_from_name(gamedb.Store, 'cd'),  
                  self.gamedb.item_from_name(gamedb.Store, 'hd')]})
        self.assertEqual(
            gplatforms,
            {'': [self.gamedb.item_from_name(gamedb.Platform, 'android')], 
             'PC': 
                 [self.gamedb.item_from_name(gamedb.Platform, 'win'),
                  self.gamedb.item_from_name(gamedb.Platform, 'linux'), 
                  self.gamedb.item_from_name(gamedb.Platform, 'mac')]})
    
    def test_x(self):
        pass