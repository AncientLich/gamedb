class StorePlat:
    def __init__(self, params):
        (self.store, self.platform, self.lang, self.link,
            self.subscription, d, m, y) = params
        if self.subscription is not None:
            self.expiredate = None
        else:
            self.expiredate = (d, m, y)



class GameView:
    def __init__(self, gameinfos, storeplats, tags):
        (self.xid, self.title, self.year, self.franchise, self.vote,
          self.priority, self.img, self.note ) = gameinfos
        self.storeplats = [StorePlat(x) for x in storeplats]
        self.tags = [x[0] for x in tags]


