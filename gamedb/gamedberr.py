# http://www.dragonball-multiverse.com/it/page-523.html#h_read

# UNEXPECTED ERROR Assert Failures:
#
# 1 = UNEXPECTED Unique costraint in gamesplat/gametag.
#     should be table1.id, table2.id (,table3.id)

import sqlite3



class ItemRequiredError(Exception):
    '''
    Error: Tried to add an item that requires an other item that does not exists
    
    This exception occurs when an item (for example a game) wants another item
    (for example a franchise to be paired with) that it does not exist in 
    database.
    So, for example, it is expected to create the franchise "Assassin's Creed"
    into 'franchise' table before adding a game (example: "Assassin's Creed 2")
    that requires that franchise.
    parameters:
    origin_table: table where the non-existing item (item2) is required.
    origin_value: the name of the concrete item that requires unixisting 'item2'
    table: table where the required item (item2) should be located
    value: expected item (item2) that is required, but it does not exist.
    Example: 
    (assuming "Assassin's Creed 2" game requiring "Assassin's Creed" franchise):
    origin_table: "game"
    origin_value: "Assassin's Creed 2"
    table: "franchise"
    value: "Assassin's Creed"
    '''
    def __init__(self, origin_table, origin_value, table, value):
        '''init parameters are the same as the class ones'''
        self.origin_table = origin_table
        self.origin_value = origin_value
        self.table = table
        self.value = value
    
    def __str__(self):
        return '{} "{}" not found in database. Required by {} "{}"'.format(
            self.table, self.value, self.origin_table, self.origin_value)



class ItemExistsError(Exception):
    '''
    Error: Tried to add an item that already exists and it is unique
    
    This exception occurs mainly when trying to add a relation in gamesplat
    or in gametag, but that relation already exists.
    For example you try to add a "Don't Starve" game for platform "linux" from
    store "steam" but it is already added.
    This means, that, for example you can't have both "demo" and "complete" game
    with the same title, from the same store and for the same platform.
    parameters:
    table = table name (exammple: 'game')
    values = list of tuples ('table.column', parameter). Values describe if the
    uniqueness is simple (list contains only one tuple) or complex (list 
    contains two or three tuples). 'Parameter' is the value that already exists
    for that column (example: if tag.name 'indie' exists than values will be
    ['tag.name', 'indie']).
    '''
    def __init__(self, table, values):
        self.table = table
        self.values = values
    
    def xstr(self):
        return '{} "{}" already exists'.format(table, values[1])



class RelationExistsError(Exception):
    '''
    Error: Tried to add a relation that already exists
    
    This is the same as ItemExistsError, but this error is focused when the
    error was raised from table 'gametag' or table 'gamesplat', where
    relations (and not actual items) are added.
    In this error you would see Actual table.parameter values that causes the
    error instead of ids internally used by those relational tables
    '''
    def __init__(self, table, values):
        self.table = table
        self.values = values
        self.msg = '"{}" relation already exists:'.format(table)
        for param, value in values:
            self.msg += '\n{} -> {}'.format(param, value)
        
    def __str__(self):
        return self.msg



class GameError(Exception):
    '''
    Error: error while using add_game on any function parameter
    '''
    
    def __init__(self, message):
        self.args = (message,)
    
    def __str__(self):
        return self.args[0]




class ItemError(Exception):
    '''
    Error: malformed item (wrong number of params, unexpected null value, etc
    '''
    
    def __init__(self, message):
        self.args = (message,)
    
    @classmethod
    def fromWrongNumpars(cls, table, expected, found):
        if expected < found:
            message = 'Too many parameters for table "{}". '.format(table)
        else:
            message = 'Not enogh parameters for table "{}". '.format(table)
        message += 'Expected {} parameters but {} found.'.format(
            expected, found)
        return cls(message)
    
    @classmethod
    def fromType(cls, table, column, expected, found):
        return cls(
            '{}.{} must contain a {} value, but a {} value '
            'found.'.format(table, column, expected, found)
        )
    
    def __str__(self):
        return self.args[0]



class UnexpectedError(Exception):
    '''
    Error that should never happen
    
    This error should never be raised, and if it occurs there are two chances:
    1) GameDB has a bug
    2) GameDB was used improperly by user
    '''
    
    def __init__(self, message):
        self.args = (message,)
    
    def __str__(self):
        return self.args[0]