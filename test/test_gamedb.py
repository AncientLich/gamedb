import os
import re
import sqlite3
import unittest
from gamedb.gamedb import GameDB
from gamedb.gamedb import _FilterGamesJoinMMR
from gamedb.gameview import StorePlat
from gamedb.gameview import GameView
import gamedb.gamedberr as gamerr



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
        tables = self.gamedb._list_tables()
        self.assertEqual(tables, 
            ['subscription', 'game', 'platform', 'store', 'gamesplat', 
             'tag', 'gametag','franchise','splatgroup']
        )
    
    # this is not an actual test.
    # it is used to generate additem_profile.txt wich contains code 
    # to include manually in gamedb.add_item()
    def disabled_test_create_additem_profilecheck(self):
        tables = self.gamedb._list_tables()
        with open('additem_profile.txt', 'w', encoding='utf-8') as fo:
            print('profile_check = {', file=fo)
            for table in tables:
                values = []
                cols = self.gamedb.cursor.execute(
                    'PRAGMA table_info({})'.format(table))
                cols = cols.fetchall()
                for _, name, xtype, _, _, _ in cols:
                    if name.lower() == 'id':
                        continue
                    if xtype == 'integer':
                        values.append((name, 'i'))
                    else:
                        values.append((name, 's'))
                # prints 'table': (('name1', 'type1'), ('name2', 'type2')),
                # where list of 'namex', 'typex' is extracted from values
                print(
                    "'{}': ({}),".format(
                        table, ', '.join(
                            ["('{}', '{}')".format(value[0], value[1])
                             for value in values]
                    )), file=fo
                )
            print('}', file=fo)
    
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
        
    def avoid_test_add_platform(self):
        for platform in ('ps3', 'ps4', 'psvita', 'win', 'linux', 'mac'):
            self.gamedb.add_platform(platform)
        value = self.gamedb.cursor.execute(
            'SELECT id, name FROM platform'
        )
        value = value.fetchall()
        self.assertEqual(value, 
            [(1, 'ps3'), (2, 'ps4'), (3, 'psvita'), (4, 'win'), 
             (5, 'linux'), (6, 'mac')]
        )
    
    def avoid_test_add_store(self):
        for i in ['psn', 'steam', 'gog', 'uplay', 'cd', 'hd']:
            self.gamedb.add_store(i)
        value = self.gamedb.cursor.execute('SELECT id, name from store')
        value = value.fetchall()
        self.assertEqual(value,
            [(1, 'psn'), (2, 'steam'), (3, 'gog'), (4, 'uplay'),
             (5, 'cd'), (6, 'hd')]
        )
    
    def add_csv_games(self):
        first = True
        self.gamedb.add_platform('ps4', 'ps')
        self.gamedb.add_platform('linux', 'pc')
        self.gamedb.add_platform('win', 'pc')
        self.gamedb.add_store('psn')
        self.gamedb.add_store('steam')
        self.gamedb.add_store('gog')
        self.gamedb.add_tag('action')
        self.gamedb.add_tag('indie')
        self.gamedb.add_tag('adventure')
        self.gamedb.add_tag('survival')
        self.gamedb.add_franchise("Don’t Starve")
        self.gamedb.add_subscription('ps+', 'psplus.png', 11, 4, 2018)
        with open('test/games01.csv', 'r', encoding='utf-8') as fi:
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
                    try:
                        self.gamedb.add_game(*params)
                    except gamerr.RelationExistsError:
                        pass
                else:
                    first = False
    
    def test_add_game_csv(self):
        self.add_csv_games()
        # ------ GAMEPSLAT -------
        gid1 = self.gamedb._sid('game', 'title', 'Bloodborne')
        gid2 = self.gamedb._sid('game', 'title', "Don’t Starve")
        pid1 = self.gamedb._sid('platform', 'name', 'ps4')
        pid2 = self.gamedb._sid('platform', 'name', 'linux')
        pid3 = self.gamedb._sid('platform', 'name', 'win')
        sid1 = self.gamedb._sid('store', 'name', 'psn')
        sid2 = self.gamedb._sid('store', 'name', 'steam')
        sid3 = self.gamedb._sid('store', 'name', 'gog')
        res = self.gamedb.cursor.execute(
            'SELECT gameid, storeid, platformid from gamesplat')
        res = res.fetchall()
        self.assertEqual( sorted(res), sorted(
            [(gid1, sid1, pid1), (gid2, sid2, pid2), (gid2, sid3, pid3)]) )
        # ---- GAMETAG ---------
        tag1a = self.gamedb._sid('tag', 'name', 'action')
        tag1b = self.gamedb._sid('tag', 'name', 'adventure')
        tag2a = self.gamedb._sid('tag', 'name', 'indie')
        tag2b = self.gamedb._sid('tag', 'name', 'survival')
        res = self.gamedb.cursor.execute(
            'SELECT gameid, tagid from gametag'
        )
        res = res.fetchall()
        self.assertEqual(sorted(res), sorted(
            [(gid1, tag1a), (gid1, tag1b), (gid2, tag2a), (gid2, tag2b)]) )
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
    
    def test_add_game_demo_repl_feature(self):
        # this test verify if a game, originally "demo", is rigtly edited to
        # "complete"
        self.gamedb.add_item('franchise', ("Don't Starve", 'ds.png'))
        self.gamedb.add_item('tag', ('survival',))
        self.gamedb.add_item('tag', ('indie',))
        self.gamedb.add_item('tag', ('co-op',))
        self.gamedb.add_item('tag', ('action',))
        self.gamedb.add_item('store', ('steam', 'steam.png', None))
        self.gamedb.add_item('store', ('psn', 'psn.png', None))
        self.gamedb.add_item('platform', ('win', 'win.png', None))
        self.gamedb.add_item('platform', ('linux', 'linux.png', None))
        self.gamedb.add_item('platform', ('mac', 'mac.png', None))
        self.gamedb.add_item('platform', ('ps4', 'ps4.png', None))
        # ---
        self.gamedb.add_game(None, 0, "Don't Starve Together", 'survival',
            "Don't Starve", 2016, 83, 'dst.png', 'en', 'steam', 'linux',
            None, None, isdemo=True)
        self.gamedb.add_game(None, 0, "Don't Starve Together", 'indie',
            "Don't Starve", 2016, 83, 'dst.png', 'en', 'steam', 'win',
            None, None, isdemo=True)
        self.gamedb.add_game(None, 0, "Don't Starve Together", 'co-op',
            "Don't Starve", 2016, 83, 'dst.png', 'en', 'steam', 'mac',
            None, None, isdemo=True)
        self.gamedb.add_game(None, 0, "Bloodborne", 'action',
            None, 2015, 83, 'bb.png', 'ita', 'psn', 'ps4',
            None, None)
        # ---
        # this should become 'complete' but other parameters should remain
        # unchanged:
        self.gamedb.add_game(None, 100, "Don't Starve Together", 'survival',
            "Don't Starve", 1800, 100, 'dst.png', 'en', 'steam', 'linux',
            None, None)
        # this should not have any effect:
        self.gamedb.add_game(None, 100, "Don't Starve Together", 'indie',
            "Don't Starve", 1800, 100, 'dst.png', 'en', 'steam', 'win',
            None, None, isdemo=True)
        # and aldo those two should not have any effect:
        self.gamedb.add_game(None, 100, "Bloodborne", 'action',
            None, 1800, 100, 'bb.png', 'ita', 'psn', 'ps4',
            None, None)
        self.gamedb.add_game(None, 100, "Bloodborne", 'action',
            None, 1500, 100, 'bb.png', 'ita', 'psn', 'ps4',
            None, None, isdemo=True)
        # -------------------------------------
        # now checking values. We will use 'gameview' wich returns all the
        # informations from a game
        game1 = self.gamedb.gameview(1)
        self.assertEqual(game1.xid, 1)
        self.assertEqual(game1.title, "Don't Starve Together")
        self.assertEqual(game1.year, 2016)
        self.assertEqual(game1.franchise, "Don't Starve")
        self.assertEqual(game1.priority, 0)
        self.assertEqual(game1.vote, 83)
        self.assertEqual(game1.img, 'dst.png')
        self.assertEqual(sorted(game1.tags),
            sorted(['survival', 'indie', 'co-op']))
        check = [
            StorePlat(
                ('steam', 'linux', 'en', None,
            None, 1, 2, 3, False)),
            StorePlat(
                ('steam', 'win', 'en', None,
            None, 1, 2, 3, True)),
            StorePlat(
                ('steam', 'mac', 'en', None,
            None, 1, 2, 3, True))
        ]
        self.compare_storeplats(game1.storeplats, check)
        # ---
        game2 = self.gamedb.gameview(2)
        self.assertEqual(game2.xid, 2)
        self.assertEqual(game2.title, "Bloodborne")
        self.assertEqual(game2.year, 2015)
        self.assertIsNone(game2.franchise)
        self.assertEqual(game2.priority, 0)
        self.assertEqual(game2.vote, 83)
        self.assertEqual(game2.img, 'bb.png')
        self.assertEqual(game2.tags,['action'])
        check = [StorePlat(
            ('psn', 'ps4', 'ita', None,
            None, 1, 2, 3, False))]
        self.compare_storeplats(game2.storeplats, check)
    
    def compare_storeplats(self, splat1_list, splat2_list):
        ''' DEBUG CODE:
        with open('debug01.txt', 'w', encoding='utf-8') as fo:
            for splat_list, lname in ((splat1_list, 'stored'), 
                                      (splat2_list, 'wanted')):
                print('###########################################', file=fo)
                print('##  {}'.format(lname), file=fo)
                print('###########################################', file=fo)
                for xid, splat in enumerate(splat_list):
                    isdemo = 'True' if splat.isdemo is True else 'False'
                    print('[{}]'.format(xid), file=fo)
                    print('store = {}\n'
                        'platform = {}\n'
                        'lang = {}\n'
                        'link = {}\n'
                        'subscription = {}\n'
                        'isdemo = {}\n'
                        'expire = '
                        '{}'.format(splat.store, splat.platform, splat.lang,
                            str(splat.link), str(splat.subscription),
                            isdemo, str(splat.expiredate)), file=fo)
        '''
        self.assertEqual(len(splat1_list), len(splat2_list))
        for splat1 in splat1_list:
            if splat1 not in splat2_list:
                isdemo = 'True' if splat1.isdemo is True else 'False'
                self.assertEqual(1,2, "\nElement in storeplat1 list is not "
                    "not contained in storeplat2.\nDetails of storeplat1:\n"
                    'store = {}\n'
                    'platform = {}\n'
                    'lang = {}\n'
                    'link = {}\n'
                    'subscription = {}\n'
                    'isdemo = {}\n'
                    'expire = '
                    '{}'.format(splat1.store, splat1.platform, splat1.lang,
                        str(splat1.link), str(splat1.subscription),
                        isdemo, str(splat1.expiredate)))
    
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
    
    def test_fgquery(self):
        # -------------------------------------------------
        #   PART 1: checking QUERY
        # -------------------------------------------------
        query, values = self.gamedb._fgquery(
            title='BloodBorne', 
            tags=['indie', 'adventure'],
            platforms=['ps4', 'win', 'linux'],
            stores=['cd', 'psn', 'steam', 'gog'],
            franchise="Starve",
            page=3
        )
        # we will strip query (removing initial and final spaces) to
        # allow a better verify
        query = query.strip()
        # the resulting query will have a sequences of subqueries wich can
        # be placed in a different order since iterating dict.values()
        # does not ensure a fixed order in python < 3.6
        # (dict.values() is used internally by gamedb._fgquery)
        # so we collect the pieces in a tmp object with the relative values
        class TmpPiece():
            def __init__(self, piece, values, *, fixed_position=None):
                self.piece = piece
                self.values = values
                self.index = None
                self.fixed_position = fixed_position
        
        org_query_pieces = [
            # this must be the first query piece (fixed_position = index 0)
            TmpPiece(
                'SELECT id, title, vote, priority, img ' 
                'FROM game WHERE lower(title) LIKE ?',
                ['%bloodborne%',],
                fixed_position = 0
            ),
            TmpPiece(
                '\nAND franchiseid IN\n'
                '(SELECT franchise.id FROM franchise WHERE '
                'franchise.name LIKE ?)',
                ['%starve%',]
            ),
            TmpPiece(
                '\nAND id IN\n'
                '(SELECT gameid from gamesplat\n'
                'INNER JOIN platform ON platform.id = gamesplat.platformid\n'
                'INNER JOIN store ON store.id = gamesplat.storeid\n'
                'WHERE (lower(platform.name) = ? OR lower(platform.name) = ? '
                'OR lower(platform.name) = ?) AND (lower(store.name) = ? OR '
                'lower(store.name) = ? OR lower(store.name) = ? '
                'OR lower(store.name) = ?))',
                ['ps4', 'win', 'linux', 'cd', 'psn', 'steam', 'gog']
            ),
            TmpPiece(
                '\nAND id IN\n'
                '(SELECT gameid from gametag\n'
                'INNER JOIN tag ON tag.id = gametag.tagid\n'
                'WHERE (lower(tag.name) = ? OR lower(tag.name) = ?))',
                ['indie', 'adventure']
            ),
            # this must be the last query piece (fixed_position = index 4)
            TmpPiece(
                '\nORDER BY title LIMIT 30 OFFSET 60',
                [],
                fixed_position = 4
            )
        ]
        sorted_query_pieces = []
        # now we do a loop of four time check, since total pieces are four
        # this will prevent infinite loop
        # the R value will be not used
        # every time a query piece is found, that piece is removed from 'query' 
        for R in range(5):
            # the 'i' index obtained from 'enumerate' is only needed when
            # removing the piece from the original list org_query_pieces
            #      org_query_pieces.pop(i)
            for i, piece in enumerate(org_query_pieces):
                if query.startswith(piece.piece):
                    piece.index = len(sorted_query_pieces)
                    # test fails if a piece with fixed position is placed
                    # in a different position than the expected one
                    if piece.fixed_position is not None:
                        self.assertEqual(piece.index, piece.fixed_position)
                    sorted_query_pieces.append(piece)
                    query = query.replace(piece.piece, '')
                    org_query_pieces.pop(i)
                    break
        # now 'query' should be empty (all pieces should be removed)
        self.assertEqual(query, '')
        # -------------------------------------------------
        #   PART 2: checking VALUES
        # -------------------------------------------------
        # also values should follow the order of the query pieces
        # so we need to build the expected_values list to be compared
        # with the values returned by gamedb._fgquery
        expected_values = []
        for piece in sorted_query_pieces:
            expected_values += piece.values
        self.assertEqual(values, expected_values)
    
    def test_filter_games(self):
        self.add_csv_games()
        bb, discard = self.gamedb.filter_games(
            title='BloodBorne',
            tags=['adventure'],
            stores=['psn'],
            platforms=['ps4']
        )
        ds, discard = self.gamedb.filter_games(
            title='Starve',
            stores=['steam'],
            platforms=['linux']
        )
        ds2, discard = self.gamedb.filter_games(
            franchise='starVe'
        )
        self.assertEqual(ds, ds2)
        self.assertEqual(ds, [(2, "Don’t Starve", 79, 0, 'dont_starve.png')])
        self.assertEqual(bb, [(1, 'Bloodborne', 92, 8, 'bloodborne.png')])
        result, count = self.gamedb.filter_games(
            count_total=True
        )
        self.assertEqual(count, 2)
    
    def test_viewgame(self):
        self.add_csv_games()
        game = self.gamedb.gameview(1)
        self.assertEqual(game.tags, ['action', 'adventure'])
        self.assertEqual(game.title, 'Bloodborne')
        self.assertEqual(game.priority, 8)
        self.assertEqual(game.vote, 92)
        self.assertEqual(game.img, 'bloodborne.png')
        self.assertEqual(len(game.storeplats), 1)
        self.assertIsNone(game.franchise)
        splat = game.storeplats[0]
        self.assertEqual(splat.subscription, 'ps+')
        self.assertEqual(splat.lang, 'it')
        self.assertEqual(splat.store, 'psn')
        self.assertEqual(splat.platform, 'ps4')
        self.assertEqual(splat.link,
            'https://store.playstation.com/it-it/product/'
            'EP9000-CUSA00207_00-BLOODBORNE0000EU?emcid=pa-st-111284'
        )
        game = self.gamedb.gameview(2)
        self.assertEqual(game.tags, ['indie', 'survival'])
        self.assertEqual(game.franchise, "Don’t Starve")
        self.assertEqual(len(game.storeplats), 2)
        splat = game.storeplats[0]
        splat2 = game.storeplats[1]
        self.assertIsNone(splat.subscription)
        self.assertIsNone(splat.link)
        self.assertEqual(splat.lang, 'en')
        self.assertEqual(splat.store, 'steam')
        self.assertEqual(splat.platform, 'linux')
        self.assertEqual(splat2.store, 'gog')
        self.assertEqual(splat2.platform, 'win')
    
    def test_upd_group_dict(self):
        d = { 'test': [(1, 2, 3)] }
        self.gamedb._upd_group_dict(d, 'test', ('a', 'b', 'c'))
        self.gamedb._upd_group_dict(d, None, ('alfa', 'beta', 'gamma'))
        self.gamedb._upd_group_dict(d, None, ('z', 'z2', 'z3'))
        self.gamedb._upd_group_dict(d, 'test2', ('e', 'f', 'g'))
        self.assertEqual(sorted(d.keys()), sorted(['test', 'test2', '']))
        self.assertEqual(d[''], [('alfa', 'beta', 'gamma'), ('z', 'z2', 'z3')])
        self.assertEqual(d['test'], [(1, 2, 3), ('a', 'b', 'c')])
        self.assertEqual(d['test2'], [('e', 'f', 'g')])
    
    def check_unpack_splat(self, table, srclist):
        result = []
        for item in srclist:
            value = (
                self.gamedb._sid(table, 'name', item),
                item, '{}.png'.format(item)
            )
            result.append(value)
        return result
    
    def test_get_grouped_splat(self):
        self.gamedb.add_group('PC')
        self.gamedb.add_group('physical')
        for table, name, groupname in [('store', 'steam', None),
                ('store', 'gog', None), ('store', 'uplay', None),
                ('store', 'cd', 'physical'), ('store', 'hd', 'physical'),
                ('platform', 'linux', 'pc'), ('platform', 'win', 'pc'),
                ('platform', 'mac', 'pc'), ('platform', 'PS4', None),
                ('platform', 'PS3', None), ('platform', 'PS Vita', None)]:
            gid = None
            if groupname is not None:
                gid = self.gamedb._sid('splatgroup', 'name', groupname)
            self.gamedb.cursor.execute(
                "INSERT INTO {} VALUES (NULL, ?,?,?)".format(table),
                (name, '{}.png'.format(name), gid)
            )
        self.gamedb.commit()
        grouped_stores, grouped_plats = self.gamedb.get_grouped_splat()
        self.assertEqual(sorted(grouped_stores.keys()), 
                         sorted(['', 'physical']))
        self.assertEqual(sorted(grouped_plats.keys()), sorted(['', 'PC']))
        self.assertEqual(grouped_stores['physical'], 
            self.check_unpack_splat('store', ['cd', 'hd']))
        self.assertEqual(grouped_stores[''], 
            self.check_unpack_splat('store', ['steam', 'gog', 'uplay']))
        self.assertEqual(grouped_plats['PC'], 
            self.check_unpack_splat('platform', ['linux', 'win', 'mac']))
        self.assertEqual(grouped_plats[''], 
            self.check_unpack_splat('platform', ['PS4', 'PS3', 'PS Vita']))
    
    def compare_dicts(self, dict1, dict2):
        self.assertEqual(len(dict1), len(dict2))
        for key, value in dict1.items():
            if key not in dict2:
                self.assertEqual(1,2, 
                    'key {} found in dict1 but not in dict2'.format(key))
            self.assertEqual(dict1[key], dict2[key])
    
    def test_add_and_list_items(self):
        self.gamedb.add_item('group', ('pc',))
        self.gamedb.add_item('group', ('physical',))
        self.gamedb.add_item('store', ('steam', 'sys/steam.png', None))
        self.gamedb.add_item('store', ('cd', 'sys/cd.png', 'physical'))
        self.gamedb.add_item('store', ('hd', 'sys/hd.png', 'physical'))
        self.gamedb.add_item('platform', ('linux', 'sys/win.png', 'pc'))
        self.gamedb.add_item('platform', ('win', 'sys/win.png', 'pc'))
        self.gamedb.add_item('platform', ('mac', 'sys/mac.png', 'pc'))
        self.gamedb.add_item('platform', ('ps4', 'sys/ps4.png', None))
        self.gamedb.commit()
        self.compare_dicts(
            self.gamedb.list_items('group'),
            {'pc': 1, 'physical': 2})
        self.compare_dicts(
            self.gamedb.list_items('store'),
            {'steam': 1, 'cd': 2, 'hd': 3})
        self.compare_dicts(
            self.gamedb.list_items('platform'),
            {'linux': 1, 'win': 2, 'mac': 3, 'ps4': 4})
    
    def test_additem_errors(self):
        with self.assertRaises(gamerr.ItemRequiredError):
            self.gamedb.add_item('store', ('steam', 'steam.png', 'pc'))
        with self.assertRaises(gamerr.ItemError) as e:
            self.gamedb.add_item('store', ('gog', 'gog.png', None, 'useless'))
            self.assertEqual(str(e),
                'Too many parameters for table "store". '
                'Expected 3 parameters but 4 found.')
        with self.assertRaises(gamerr.ItemError):
            self.gamedb.add_item('group', ('pc', None))
        with self.assertRaises(gamerr.ItemError) as e:
            self.gamedb.add_item('gamesplat', ('gog', 'linux'))
            self.assertEqual(str(e),
                'Not enogh parameters for table "gamesplat". '
                'Expected 7 parameters but 2 found.')
        self.gamedb.add_item('group', ('pc',))
        with self.assertRaises(gamerr.ItemExistsError):
            self.gamedb.add_item('group', ('pc',))
        with self.assertRaises(gamerr.ItemError) as e:
            self.gamedb.add_item('store', (None, 'gog.png', None))
            self.assertEqual(str(e),
                'Unexpected NULL value: store.name')
    
    