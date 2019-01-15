import os
import re
import sqlite3
import attr
import gamedb.items
import gamedb.errors
import gamedb.cnv
from datetime import date
from functools import partial
from collections import OrderedDict


#--------


'''
Class that manages all database operations for games.db
'''
class GameDB:
    def __init__(self, dbname):
        '''Intialize database (database_file)'''
        self.conn = sqlite3.connect(dbname)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        # cache1 (cache for names)
        self.cache_names = {}
        # cache2 (cache for ids)
        self.cache_ids = {}
        self._tables = self._check_tables()
        self._create_tables()
    
    # on startup check wich tables exist in DB and return a set with the
    # name of all tables
    def _check_tables(self):
        ts = self.cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table'")
        ts = ts.fetchall()
        tables = set()
        for t in ts:
            t = dict(t)
            t = t['name']
            if 'sqlite' not in t:
                tables.add(t)
        return tables
    
    # create tables required from dictionary if not already added in DB
    def _create_tables(self):
        modified = False
        clsrules = gamedb.items.rules_ordered()
        for cls, rule in clsrules.items():
            if cls.tablename not in self._tables:
                modified = True
                cmd = gamedb.cnv.mk_table_cmd(cls, rule)
                self._tables.add(cls.tablename)
                self.cursor.execute(cmd)
        
        if modified:
            self.conn.commit()
    
    def commit(self):
        self.conn.commit()
    
    def close(self):
        '''close database connection'''
        self.conn.close()
