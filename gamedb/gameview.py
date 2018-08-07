'''
This class defines a single object in GameView.storeplats

a StorePlat is a combination of store+platform+... so it describe a single
entry in the gamesplat relation table (but in an human-understandable way)

properties:
store = store name or imagename
platform = platform image or imagename
lang = 'main' language of the game for that 'store, platform'
link = download link for the game for that 'store, platform'
subscription = subscription name or imagename (if any)
expiredate = tuple (day, month, year) or None (if game does not expire)
'''
class StorePlat:
    def __init__(self, params):
        '''a StorePlat object is inited by GameView class
        
        params: a tuple (or list) of values must be passed:
        (store, platform, lang, link, subscription, d, m, y) where:
        store, platform, lang are strings
        link, subscription can be string or None (download link, subscription)
        d, m ,y are numbers or None (if subscription is None: d, m, y 
        will be ignored). d=day, m=month, y=year (expiration data)
        '''
        (self.store, self.platform, self.lang, self.link,
            self.subscription, d, m, y, self.isdemo) = params
        self.isdemo = bool(self.isdemo)
        self.expiredate = None if self.subscription is None else (d, m, y)
    
    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return ((self.store, self.platform, self.lang, self.link,
                 self.subscription, self.isdemo, self.expiredate) ==
                (other.store, other.platform, other.lang, other.link,
                 other.subscription, other.isdemo, other.expiredate))



'''
This class describes full informations for a single game

properties:
xid = game ID
title = game title
year = game year
franchise = game franchise (if any)
vote = game vote (metacritic)
priority = game priority (higher value = sooner you want to play it)
img = game image name (text)
note = game note (text)
storeplats = list of StorePlats for the game (see StorePlat class documentation)
tags = list of tags (list of strings)
'''
class GameView:
    def __init__(self, gameinfos, storeplats, tags):
        '''GameView is inited by GameDB.gameview function
        
        params:
        gameinfos -> list/tuple of parameters (see note (1))
        storeplats -> list/tuple of parameters (see note (2))
        tags -> list/tuple of tags (list of strings)
        
        Notes:
        (1) gameinfos is calculated by gamedb.gamedb.gameview when
        executing a SELECT query FROM game table:
        gameinfos must be a tuple (or list) of those values:
        (id, title, year, franchise, vote, priority, img, note) where:
        id = game id (integer)
        title = game title (string)
        franchise = game franchise (string or None)
        vote = game metacritic vote (integer or None)
        priority = game priority (integer or None)
        img = game image name (text)
        note = (text or None)
        
        (2) storeplats is calculated by gamedb.gamedb.gameview when
        executing a SELECT query FROM gamesplat table:
        storeplats is a list of tuple. Every tuple in list must contains
        all values required by 'params' in StorePlat(params) initialization.
        See StorePlat for more details
        '''
        (self.xid, self.title, self.year, self.franchise, self.vote,
          self.priority, self.img, self.note ) = gameinfos
        self.storeplats = [StorePlat(x) for x in storeplats]
        self.tags = tags


