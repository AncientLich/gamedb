import unittest
import os
import re
import sqlite3
from gamedb.test_gamedb import TestGameDB



if __name__ == '__main__':
    try:
        os.remove('test.db')
    except FileNotFoundError:
        pass
    unittest.main()
